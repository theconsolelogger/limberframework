"""Available stores for handling data in a cache."""
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

        Args:
            key: Identifier of data in cache.

        Returns:
            dict: A dictionary containing the data for the key.
        """

    @abstractmethod
    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
        """Store data in cache if it does not already exist.

        Args:
            key: Identifier of data in cache.
            value: Data to store in cache.
            expires_at: Time of when the data expires.

        Returns:
            bool: True if successfully added, False otherwise.
        """

    @abstractmethod
    async def put(self, key: str, value: str, expires_at: datetime) -> bool:
        """Store data in cache, overriding any existing data.

        Args:
            key: Identifier of data in cache.
            value: Data to store in cache.
            expires_at: Time of when the data expires.

        Returns:
            bool: True if successfully update, False otherwise.
        """

    @staticmethod
    def payload(data: any = None, expires_at: datetime = None) -> Dict:
        """Generate payload of cache data.

        Args:
            data: cache data.
            expires_at: expiry time of cache.

        Returns:
            dict: cache data.
        """
        return {"data": data, "expires_at": expires_at}

    @staticmethod
    def has_expired(expires_at: datetime) -> bool:
        """Check if a datetime has expired.

        Args:
            expires_at: The datetime to check.

        Returns:
            bool: True if expired, False otherwise.
        """
        if datetime.now() >= expires_at:
            return True
        return False

    @staticmethod
    def encode(value: str, expires_at: datetime) -> str:
        """Encode the value for storing in the cache.

        Converts the datetime to an iso format
        string and combines with the value.

        Args:
            value: value of the data.
            expires_at: datetime of when the data is considered expired.

        Returns:
            str: The encoded value.
        """
        return expires_at.isoformat() + "," + value

    @staticmethod
    def decode(contents: str) -> Dict:
        """Decode the value from storage.

        Extracts the datetime and value from the stored string.

        Args:
            contents: The value to decode.

        Returns:
            dict: Contains the expires_at datetime and value.
        """
        contents_list = contents.split(",", 1)
        expires_at = datetime.fromisoformat(contents_list[0])

        return {"value": contents_list[1], "expires_at": expires_at}

    @classmethod
    def process(cls, contents: str) -> Dict:
        """Process the stored cache data.

        Decodes the data and returns in a standard format.

        Args:
            contents: The data to process.

        Returns:
            dict: Dictionary containing the data.
        """
        if not contents:
            return cls.payload()

        contents = contents.decode()

        decoded_contents = cls.decode(contents)
        return cls.payload(
            decoded_contents["value"], decoded_contents["expires_at"]
        )

    def __getitem__(self, key: str) -> Dict:
        """Retrieve store data for a key.

        Args:
            key: Identifier of the data.

        Returns:
            dict: The data stored in the cache.
        """
        return self.get(key)


class FileStore(Store):
    """Handles storing and retrieving data from the file system.

    Attributes:
        directory: System path to cache folder.
    """

    def __init__(self, directory: str) -> None:
        """Establish the store.

        Args:
            directory: System path to cache folder.
        """
        self.directory = directory

    def path(self, key: str) -> str:
        """Generate the system path to the cache file.

        Args:
            key: Cache key.

        Returns:
            str: Path to the cache file.
        """
        hasher = Hasher("sha1")
        return self.directory + "/" + hasher(key)

    async def get(self, key: str) -> Dict:
        """Retrieve stored data for a key.

        Args:
            key: key for cached data.

        Returns:
            dict: The stored data for the key.
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

        Args:
            key: Key for data.
            value: The data to store.
            expires_at: Number of seconds the data is valid for.

        Returns:
            bool: True if successfully stored, False otherwise.
        """
        path = self.path(key)

        if not FileSystem.has_file(path):
            return False

        return await self.put(key, value, expires_at)

    async def put(self, key: str, value: str, expires_at: datetime) -> bool:
        """Add data to cache storage, overriding any existing data.

        Args:
            key: Key for data.
            value: The data to store.
            expires_at: Number of seconds the data is valid for.

        Returns:
            bool: True if successfully update, False otherwise.
        """
        path = self.path(key)

        contents = self.encode(value, expires_at)
        FileSystem.write_file(path, contents)

        return True


class RedisStore(Store):
    """Handles storing and retrieving data from a Redis server.

    Attributes:
        redis: A Redis connection.
    """

    def __init__(self, redis: Redis) -> None:
        """Establish the redis connection.

        Args:
            redis: A Redis connection.
        """
        self.redis = redis

    async def get(self, key: str) -> Dict:
        """Retrieve a value for a key in the cache.

        Args:
            key: key to retrieve value for.

        Returns:
            dict: Dictionary containing the value.
        """
        contents = self.redis.get(key)
        return self.process(contents)

    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
        """Add a new key and value to the cache.

        Args:
            key: The new key.
            value: Data to add for the key.
            expires_at: datetime when the data is considered expired.

        Returns:
            bool: True if successfully added, False otherwise.
        """
        return await self.put(key, value, expires_at, nx=True)

    async def put(
        self, key: str, value: str, expires_at: datetime, **kwargs
    ) -> bool:
        """Update a value for a key in the cache.

        Args:
            key: The key to update.
            value: The new value to stored for the key.
            expires_at: datetime of when the data is considered expired.

        Returns:
            bool: True if successfully updated, False otherwise.
        """
        contents = self.encode(value, expires_at)
        number_seconds = expires_at - datetime.now()

        return self.redis.set(key, contents, ex=number_seconds, **kwargs)


class AsyncRedisStore(Store):
    """Handles storing and retrieving data from a Redis server asynchronously.

    Attributes:
        redis: The Redis connection.
    """

    def __init__(self, redis: RedisConnection) -> None:
        """Establish the redis connection.

        Args:
            redis: A redis connection.
        """
        self.redis = redis

    async def get(self, key: str) -> Dict:
        """Retrieve a value for a key from the cache.

        Args:
            key: The key to retrieve a value for.

        Returns:
            dict: Dictionary containing the value.
        """
        contents = await self.redis.get(key)
        return self.process(contents)

    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
        """Add a new key and value to the cache.

        Args:
            key: The new key.
            value: The value to store for the key.
            expires_at: Datetime when the value is considered expired.

        Returns:
            bool: True if successfully added, Fale otherwise.
        """
        key_exists = await self.redis.exists(key)

        if key_exists:
            return False

        return await self.put(key, value, expires_at)

    async def put(
        self, key: str, value: str, expires_at: datetime, **kwargs
    ) -> bool:  # noqa: D202
        """Update a value for a key in the cache.

        Args:
            key: The key to update.
            value: The new value.
            expires_at: Datetime when the value is considered expired.

        Returns:
            bool: True if successfully update, False otherwise.
        """

        contents = self.encode(value, expires_at)

        await self.redis.set(key, contents)
        await self.redis.expireat(key, int(expires_at.timestamp()))

        return True

    async def __getitem__(self, key: str) -> Dict:
        """Retrieve a value for a key from the cache.

        Args:
            key: The key to retrieve a value for.

        Returns:
            dict: Dictionary containing the value.
        """
        return await self.get(key)


class MemcacheStore(Store):
    """Handles retrieving and storing values in memcache.

    Attributes:
        client: The connection to the memcache.
    """

    def __init__(self, client: Client) -> None:
        """Establish the connection to the memcache.

        Args:
            client: A connection to the memcache.
        """
        self.client = client

    async def get(self, key: str) -> Dict:
        """Retrieve a value for a key from the cache.

        Args:
            key: The key to retrieve a value for.

        Returns:
            dict: Dictionary containing the value.
        """
        contents = self.client.get(key)
        return self.process(contents)

    async def add(self, key: str, value: str, expires_at: datetime) -> bool:
        """Add a new key and value to the cache.

        Args:
            key: The new key.
            value: Value for the key.
            expires_at: Datetime when the value is considered expired.

        Returns:
            bool: True if successfully added, False otherwise.
        """
        contents = self.client.get(key)

        if contents:
            return False

        return await self.put(key, value, expires_at)

    async def put(self, key: str, value: str, expires_at: datetime) -> bool:
        """Update a key with a new value in the cache.

        Args:
            key: The key to update.
            value: Value for the key.
            expires_at: Datetime when the value is considered expired.

        Returns:
            bool: True if successfully added, False otherwise.
        """
        contents = self.encode(value, expires_at)
        number_seconds = ceil((expires_at - datetime.now()).total_seconds())

        return self.client.set(key, contents, expire=number_seconds)


async def make_store(config: Dict) -> Store:
    """Establish a cache store.

    Args:
        config: Settings for the store.

    Returns:
        Store: The created Store.

    Raises:
        ValueError: If the store driver in `config` is not recognised.
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
