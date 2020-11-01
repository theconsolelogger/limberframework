from unittest.mock import AsyncMock, Mock, patch

from aioredlock import Aioredlock
from pytest import mark, raises

from limberframework.cache.lockers import AsyncRedisLocker, make_locker


def test_create_async_redis_locker():
    mock_locker = Mock()

    locker = AsyncRedisLocker(mock_locker)

    assert locker.lock_manager == mock_locker


@mark.parametrize("key,expires_in", [("resource", 10), ("cache", 0)])
@mark.asyncio
async def test_async_redis_locker_lock(key, expires_in):
    mock_aioredlock = Mock()
    mock_aioredlock.lock = AsyncMock()

    locker = AsyncRedisLocker(mock_aioredlock)
    locker.lock_manager = mock_aioredlock

    await locker.lock(key, expires_in)

    mock_aioredlock.lock.assert_called_once_with(
        f"lock-{key}", lock_timeout=expires_in
    )
    assert locker._locks[key] == mock_aioredlock.lock.return_value


@mark.asyncio
async def test_async_redis_locker_unlock():
    key = "resource"

    mock_aioredlock = Mock()
    mock_aioredlock.unlock = AsyncMock()
    mock_lock = Mock()

    locker = AsyncRedisLocker(mock_aioredlock)
    locker._locks[key] = mock_lock

    await locker.unlock(key)

    mock_aioredlock.unlock.assert_called_once_with(mock_lock)


@patch("limberframework.cache.lockers.AsyncRedisLocker")
@mark.asyncio
async def test_make_locker_without_password(mock_asyncredislocker):
    config = {
        "locker": "asyncredis",
        "host": "localhost",
        "port": 1234,
        "db": 0,
        "password": None,
        "locker_retry_count": 1,
    }

    await make_locker(config)

    mock_asyncredislocker.assert_called_once_with(
        Aioredlock(
            [
                {
                    "host": config["host"],
                    "port": config["port"],
                    "db": config["db"],
                    "password": config["password"],
                }
            ],
            retry_count=config["locker_retry_count"],
        )
    )


@patch("limberframework.cache.lockers.AsyncRedisLocker")
@mark.asyncio
async def test_make_locker_with_password(mock_asyncredislocker):
    config = {
        "locker": "asyncredis",
        "host": "localhost",
        "port": 1234,
        "db": 0,
        "password": "test",
        "locker_retry_count": 1,
    }

    await make_locker(config)

    mock_asyncredislocker.assert_called_once_with(
        Aioredlock(
            [
                {
                    "host": config["host"],
                    "port": config["port"],
                    "db": config["db"],
                    "password": config["password"],
                }
            ],
            retry_count=1,
        )
    )


@mark.asyncio
async def test_make_locker_with_invalid_locker():
    config = {"locker": "test"}

    with raises(
        ValueError, match=f"Unsupported cache locker {config['locker']}."
    ):
        await make_locker(config)
