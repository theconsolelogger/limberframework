"""Cache

Classes:
- Cache: handles interacting with the store.
"""
from datetime import datetime

from limberframework.cache.stores import Store


class Cache:
    """Handles retrieving and storing
    data in the store.

    Attributes:
    _store Store -- Store object.
    _key str -- identifier for the data in storage.
    value str -- value of data.
    expires_at datetime -- time when the data expires.
    """

    def __init__(self, store: Store) -> None:
        """Establishes the cache.

        Arguments:
        store Store -- Store object.
        key str -- identifier for the data in storage.
        """
        self._store: Store = store
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
