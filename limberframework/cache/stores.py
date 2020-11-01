"""Store

Classes:
- Store: Base class for a store.
- FileStore: handles storing data in files.

Functions:
- make_store: factory function for creating a store.
"""
from abc import ABCMeta, abstractmethod
from datetime import datetime
from math import ceil
from typing import Dict

from aioredis import RedisConnection, create_redis
from pymemcache.client.base import Client
from redis import Redis

from limberframework.filesystem.filesystem import FileSystem
from limberframework.hashing.hashers import Hasher


class Store(metaclass=ABCMeta):
    """Base class for a store."""

    @abstractmethod
    async def get(self, key: str) -> Dict:
        """Retrieve data from cache.

        Arguments:
        key str -- identifier of data in cache.

        Returns dict.
        """

    @abstractmethod
    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
        """Store data in cache if it does not already exist.

        Arguments:
        key str -- identifier of data in cache.
        value str -- data to store in cache.
        expires_at datetime -- time of when the data expires.

        Returns bool.
        """

    @abstractmethod
    async def put(self, key: str, value: str, expires_at: datetime) -> bool:
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
        return {"data": data, "expires_at": expires_at}

    @staticmethod
    def has_expired(expires_at: datetime) -> bool:
        if datetime.now() >= expires_at:
            return True
        return False

    @staticmethod
    def encode(value: str, expires_at: datetime) -> str:
        return expires_at.isoformat() + "," + value

    @staticmethod
    def decode(contents: str) -> Dict:
        contents_list = contents.split(",", 1)
        expires_at = datetime.fromisoformat(contents_list[0])

        return {"value": contents_list[1], "expires_at": expires_at}

    @classmethod
    def process(cls, contents: str) -> Dict:
        if not contents:
            return cls.payload()

        contents = contents.decode()

        decoded_contents = cls.decode(contents)
        return cls.payload(
            decoded_contents["value"], decoded_contents["expires_at"]
        )

    def __getitem__(self, key: str) -> Dict:
        """Retrieves store data for a key.

        Arguments:
        key str -- identifier of the data.

        Returns dict.
        """
        return self.get(key)


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
        hasher = Hasher("sha1")
        return self.directory + "/" + hasher(key)

    async def get(self, key: str) -> Dict:
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

        decoded_contents = self.decode(contents)

        if self.has_expired(decoded_contents["expires_at"]):
            FileSystem.remove(path)
            return self.payload()

        return self.payload(
            decoded_contents["value"], decoded_contents["expires_at"]
        )

    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
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

        return await self.put(key, value, expires_at)

    async def put(self, key: str, value: str, expires_at: datetime) -> bool:
        """Add data to cache storage, overriding any existing data.

        Arguments:
        key str -- key for data.
        value str -- the data to store.
        expires_at datetime -- number of seconds the data is valid for.
        path str [optional] -- system path to cache file.

        Returns bool.
        """
        path = self.path(key)

        contents = self.encode(value, expires_at)
        FileSystem.write_file(path, contents)

        return True


class RedisStore(Store):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> Dict:
        contents = self.redis.get(key)
        return self.process(contents)

    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
        return await self.put(key, value, expires_at, nx=True)

    async def put(
        self, key: str, value: str, expires_at: datetime, **kwargs
    ) -> bool:
        contents = self.encode(value, expires_at)
        number_seconds = expires_at - datetime.now()

        return self.redis.set(key, contents, ex=number_seconds, **kwargs)


class AsyncRedisStore(Store):
    def __init__(self, redis: RedisConnection) -> None:
        self.redis = redis

    async def get(self, key: str):
        contents = await self.redis.get(key)
        return self.process(contents)

    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
        key_exists = await self.redis.exists(key)

        if key_exists:
            return False

        return await self.put(key, value, expires_at)

    async def put(self, key: str, value: str, expires_at: datetime, **kwargs):
        contents = self.encode(value, expires_at)

        await self.redis.set(key, contents)
        await self.redis.expireat(key, int(expires_at.timestamp()))

        return True

    async def __getitem__(self, key: str) -> Dict:
        return await self.get(key)


class MemcacheStore(Store):
    def __init__(self, client: Client) -> None:
        self.client = client

    async def get(self, key: str) -> Dict:
        contents = self.client.get(key)
        return self.process(contents)

    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
        contents = self.client.get(key)

        if contents:
            return False

        return await self.put(key, value, expires_at)

    async def put(self, key: str, value: str, expires_at: datetime) -> bool:
        contents = self.encode(value, expires_at)
        number_seconds = ceil((expires_at - datetime.now()).total_seconds())

        return self.client.set(key, contents, expire=number_seconds)


async def make_store(config: Dict) -> Store:
    """Factory function to establish a cache store.

    Arguments:
    config Dict -- settings for the store.

    Returns:
    Store object.
    """
    if config["driver"] == "file":
        return FileStore(config["path"])
    if config["driver"] == "redis":
        return RedisStore(
            Redis(
                host=config["host"],
                port=config["port"],
                db=config["db"],
                password=config["password"],
            )
        )
    if config["driver"] == "asyncredis":
        redis = await create_redis(
            f"redis://{config['host']}:{config['port']}",
            password=config["password"],
            db=config["db"],
        )
        return AsyncRedisStore(redis)
    if config["driver"] == "memcache":
        return MemcacheStore(Client((config["host"], config["port"])))

    raise ValueError(f"Unsupported cache driver {config['driver']}.")
