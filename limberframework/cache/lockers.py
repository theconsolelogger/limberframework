"""Lockers

Classes:
- Locker: Abstract base class for lockers.
- AsyncRedisLocker: Async locker for redis.
"""
from abc import ABCMeta, abstractmethod
from typing import Dict

from aioredlock import Aioredlock


class Locker(metaclass=ABCMeta):
    """Abstract base class for a locker.

    Attributes:
    _locks dict -- list of set locks.
    """

    def __init__(self):
        """Establishes the set locks."""
        self._locks = {}

    @abstractmethod
    def lock(self, key: str) -> None:
        """Locks a key in the store.

        Arguments:
        key str -- the key to lock.
        """

    @abstractmethod
    def unlock(self, key: str) -> None:
        """Unlocks a key in the store.

        Arguments:
        key str -- the key to unlock.
        """


class AsyncRedisLocker(Locker):
    """Locker for a Redis database with an async connection."""

    def __init__(self, host: str, port: str, db: str, password: str):
        """Establishes the connection to the Redis database.

        Arguments:
        host str -- machine which the Redis database is on.
        port str -- port to communicate with the Redis database.
        db str -- the Redis database to use.
        password str -- password to authenticate with the Redis database.
        """
        connection = {"host": host, "port": port, "db": db}

        if password:
            connection["password"] = password

        self.lock_manager = Aioredlock([connection], retry_count=1)

        super().__init__()

    async def lock(self, key: str, expires_in: int = 10) -> None:
        """Locks a key in the Redis database.

        Arguments:
        key str -- the key to lock.
        expires_in int -- number of seconds the lock is valid for.
        """
        lock = await self.lock_manager.lock(
            f"lock-{key}", lock_timeout=expires_in
        )
        self._locks[key] = lock

    async def unlock(self, key: str) -> None:
        """Unlocks a key in the Redis database.

        Arguments:
        key str -- the key to unlock.
        """
        lock = self._locks[key]
        await self.lock_manager.unlock(lock)


async def make_locker(config: Dict) -> Locker:
    """Factory function to create a locker.

    Arguments:
    config dict -- configuration settings for the locker.

    Returns Locker object.
    """
    if config["locker"] == "asyncredis":
        return AsyncRedisLocker(
            config["host"], config["port"], config["db"], config["password"]
        )

    ValueError(f"Unsupported cache locker {config['locker']}.")
