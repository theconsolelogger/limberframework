from datetime import datetime
from unittest.mock import AsyncMock, Mock

from pytest import fixture, mark, raises

from limberframework.cache.cache import Cache
from limberframework.cache.exceptions import CacheLockError


@fixture
def mock_store():
    return AsyncMock()


@mark.asyncio
async def test_load(mock_store):
    data = {"data": "test", "expires_at": datetime.now()}
    mock_store.get.return_value = data

    cache = Cache(mock_store)
    await cache.load("test_cache")

    assert cache._key == "test_cache"
    assert cache.value == data["data"]
    assert cache.expires_at == data["expires_at"]


@mark.parametrize(
    "value,expires_at,updated",
    [
        ("test", datetime.now(), True),
        (None, None, False),
        (None, datetime.now(), False),
        ("test", None, False),
    ],
)
@mark.asyncio
async def test_update(value, expires_at, updated, mock_store):
    mock_store.put.return_value = True
    key = "test_key"

    cache = Cache(mock_store)
    cache._key = key
    cache.value = value
    cache.expires_at = expires_at

    response = await cache.update()

    assert response == updated


@mark.asyncio
async def test_lock():
    key = "test"
    mock_locker = Mock()
    mock_locker.lock = AsyncMock()

    cache = Cache(Mock(), mock_locker)
    cache._key = key

    await cache.lock()

    mock_locker.lock.assert_called_once_with(key)


@mark.asyncio
async def test_lock_key_not_set():
    cache = Cache(Mock(), Mock())

    with raises(CacheLockError, match="Cannot set lock for key None."):
        await cache.lock()


@mark.asyncio
async def test_lock_locker_not_set():
    cache = Cache(Mock())

    with raises(CacheLockError, match="Cannot set lock with locker None."):
        await cache.lock()


@mark.asyncio
async def test_unlock():
    key = "test"
    mock_locker = Mock()
    mock_locker.unlock = AsyncMock()

    cache = Cache(Mock(), mock_locker)
    cache._key = key

    await cache.unlock()

    mock_locker.unlock.assert_called_once_with(key)


@mark.asyncio
async def test_unlock_key_not_set():
    mock_locker = Mock()
    mock_locker.unlock = AsyncMock()

    cache = Cache(Mock(), mock_locker)

    with raises(CacheLockError, match="Cannot unset lock for key None."):
        await cache.unlock()


@mark.asyncio
async def test_unlock_locker_not_set():
    cache = Cache(Mock())

    with raises(CacheLockError, match="Cannot unset lock with locker None."):
        await cache.unlock()


@mark.asyncio
async def test_secure():
    mock_lock = AsyncMock()
    mock_unlock = AsyncMock()

    cache = Cache(Mock())
    cache.lock = mock_lock
    cache.unlock = mock_unlock

    async with cache.secure():
        pass

    mock_lock.assert_called_once()
    mock_unlock.assert_called_once()
