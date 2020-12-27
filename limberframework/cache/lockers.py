"""Available Lockers to lock keys in the cache."""
from abc import ABCMeta, abstractmethod
from typing import Dict

from aioredlock import Aioredlock


class Locker(metaclass=ABCMeta):
    """Abstract base class for a locker.

    Attributes:
        _locks: Dictionary of set locks.
    """

    def __init__(self):
        """Establish the set locks."""
        self._locks = {}

    @abstractmethod
    def lock(self, key: str) -> None:
        """Locks a key in the store.

        Args:
            key: The key to lock.
        """

    @abstractmethod
    def unlock(self, key: str) -> None:
        """Unlocks a key in the store.

        Args:
            key: The key to unlock.
        """


class AsyncRedisLocker(Locker):
    """Locker for a Redis database with an async connection.

    Attributes:
        lock_manager: mechanism used to lock keys in the cache.
    """

    def __init__(self, lock_manager: Aioredlock) -> None:
        """Establish the connection to the Redis database.

        Args:
            lock_manager: An Aioredlock connection.
        """
        self.lock_manager = lock_manager

        super().__init__()

    async def lock(self, key: str, expires_in: int = 10) -> None:
        """Locks a key in the Redis database.

        Args:
            key: The key to lock.
            expires_in: Number of seconds the lock is valid for.
        """
        lock = await self.lock_manager.lock(
            f"lock-{key}", lock_timeout=expires_in
        )
        self._locks[key] = lock

    async def unlock(self, key: str) -> None:
        """Unlocks a key in the Redis database.

        Args:
            key: The key to unlock.
        """
        lock = self._locks[key]
        await self.lock_manager.unlock(lock)


async def make_locker(config: Dict) -> Locker:
    """Create a locker.

    Args:
        config: Configuration settings for the locker.

    Returns:
        The created Locker instance.

    Raises:
        ValueError: If the locker is not recognised in `config`.
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
