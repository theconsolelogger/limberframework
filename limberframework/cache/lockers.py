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

    def __init__(self, lock_manager: Aioredlock) -> None:
        """Establishes the connection to the Redis database.

        Arguments:
        lock_manager aioredlock.Aioredlock -- an Aioredlock connection.
        """
        self.lock_manager = lock_manager

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
        connection = {
            "host": config["host"],
            "port": config["port"],
            "db": config["db"],
            "password": config["password"],
        }

        return AsyncRedisLocker(
            Aioredlock([connection], retry_count=config["locker_retry_count"])
        )

    raise ValueError(f"Unsupported cache locker {config['locker']}.")
