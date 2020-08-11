"""Store

Classes:
- Store: Base class for a store.
- FileStore: handles storing data in files.

Functions:
- make_store: factory function for creating a store.
"""
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Dict
from limberframework.hashing.hashers import Hasher
from limberframework.filesystem.filesystem import FileSystem

class Store(metaclass=ABCMeta):
    """Base class for a store."""
    @abstractmethod
    def get(self, key: str) -> Dict:
        """Retrieve data from cache.

        Arguments:
        key str -- identifier of data in cache.

        Returns dict.
        """

    @abstractmethod
    def add(self, key: str, value: str, expires_at: datetime) -> bool:
        """Store data in cache if it does not already exist.

        Arguments:
        key str -- identifier of data in cache.
        value str -- data to store in cache.
        expires_at datetime -- time of when the data expires.

        Returns bool.
        """

    @abstractmethod
    def put(self, key: str, value: str, expires_at: datetime) -> bool:
        """Store data in cache, overriding any existing data.

        Arguments:
        key str -- identifier of data in cache.
        value str -- data to store in cache.
        expires_at datetime -- time of when the data expires.

        Returns bool.
        """

    @staticmethod
    def payload(data: any = None, expires_at: datetime = None) -> Dict:
        """Generates payload of cache data.

        Arguments:
        data any -- cache data.
        expires_at datetime -- expiry time of cache.

        Returns:
        dict -- cache data.
        """
        return {'data': data, 'expires_at': expires_at}

class FileStore(Store):
    """Handles storing and retrieving data from the file system.

    Attributes:
    directory str -- system path to cache folder.
    """
    def __init__(self, directory: str) -> None:
        """Establishes the store.

        Arguments:
        directory str -- system path to cache folder.
        """
        self.directory = directory

    def path(self, key: str) -> str:
        """Generates the system path to the cache file.

        Arguments:
        key str -- cache key.

        Returns:
        str -- path to the cache file.
        """
        hasher = Hasher('sha1')
        return self.directory + '/' + hasher.hash(key)

    def get(self, key: str) -> Dict:
        """Retrieves stored data for a key.

        Arguments:
        key str -- key for cached data.

        Returns dict.
        """
        path = self.path(key)

        try:
            contents = FileSystem.read_file(path)
        except FileNotFoundError:
            return self.payload()

        contents_list = contents.split(',', 1)
        expires_at = datetime.fromisoformat(contents_list[0])

        # If cache has expired remove from storage.
        if datetime.now() >= expires_at:
            FileSystem.remove(path)
            return self.payload()

        return self.payload(contents_list[1], expires_at)

    def add(self, key: str, value: str, expires_at: datetime) -> bool:
        """Add data to cache storage if it does not already exist.

        Arguments:
        key str -- key for data.
        value str -- the data to store.
        expires_at datetime -- number of seconds the data is valid for.

        Returns bool.
        """
        path = self.path(key)

        if not FileSystem.has_file(path):
            return False

        return self.put(key, value, expires_at)

    def put(self, key: str, value: str, expires_at: datetime) -> bool:
        """Add data to cache storage, overriding any existing data.

        Arguments:
        key str -- key for data.
        value str -- the data to store.
        expires_at datetime -- number of seconds the data is valid for.
        path str [optional] -- system path to cache file.

        Returns bool.
        """
        path = self.path(key)

        contents = expires_at.isoformat() + ',' + value
        FileSystem.write_file(path, contents)

        return True

    def __getitem__(self, key: str) -> Dict:
        """Retrieves store data for a key.

        Arguments:
        key str -- identifier of the data.

        Returns dict.
        """
        return self.get(key)

def make_store(config: Dict) -> Store:
    """Factory function to establish a cache store.

    Arguments:
    config Dict -- settings for the store.

    Returns:
    Store object.
    """
    if config['driver'] == 'file':
        return FileStore(config['path'])

    raise ValueError(f"Unsupported cache driver {config['driver']}.")
