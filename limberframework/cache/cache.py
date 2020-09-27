"""Cache

Classes:
- Cache: handles interacting with the store.
"""
from contextlib import asynccontextmanager
from datetime import datetime

from limberframework.cache.exceptions import CacheLockError
from limberframework.cache.lockers import Locker
from limberframework.cache.stores import Store


class Cache:
    """Handles retrieving and storing
    data in the store.

    Attributes:
    _store Store -- Store object.
    _locker Locker -- Locker object.
    _key str -- identifier for the data in storage.
    value str -- value of data.
    expires_at datetime -- time when the data expires.
    """

    def __init__(self, store: Store, locker: Locker = None) -> None:
        """Establishes the cache.

        Arguments:
        store Store -- Store object.
        locker Locker -- Locker object.
        """
        self._store: Store = store
        self._locker: Locker = locker
        self._key: str = None
        self.value: str = None
        self.expires_at: datetime = None

    async def load(self, key: str) -> None:
        """Retrieves data from storage.

        Arguments:
        key str -- identifier of the data to load.
        """
        storage = await self._store.get(key)

        self._key = key
        self.value = storage["data"]
        self.expires_at = storage["expires_at"]

    async def update(self) -> bool:
        """Stores the data, requires value
        and expires_at to have a value.
        """
        if not self.value or not self.expires_at:
            return False
        return await self._store.put(self._key, self.value, self.expires_at)

    async def lock(self):
        """Locks the key in the store."""
        if not self._locker:
            raise CacheLockError(
                f"Cannot set lock with locker {str(self._locker)}."
            )

        if not self._key:
            raise CacheLockError(f"Cannot set lock for key {str(self._key)}.")

        await self._locker.lock(self._key)

    async def unlock(self):
        """Unlocks the key in the store."""
        if not self._locker:
            raise CacheLockError(
                f"Cannot unset lock with locker {str(self._locker)}."
            )

        if not self._key:
            raise CacheLockError(
                f"Cannot unset lock for key {str(self._key)}."
            )

        await self._locker.unlock(self._key)

    @asynccontextmanager
    async def secure(self):
        """Context manager for handling locking a key in the store."""
        await self.lock()
        try:
            yield
        finally:
            await self.unlock()
