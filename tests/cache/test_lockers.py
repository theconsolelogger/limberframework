from unittest.mock import AsyncMock, Mock, patch

from pytest import mark, raises

from limberframework.cache.lockers import AsyncRedisLocker, make_locker


@mark.parametrize(
    "connection",
    [
        {"host": "localhost", "port": 1234, "db": 0, "password": None},
        {"host": "127.0.0.1", "port": 4321, "db": 1, "password": "password"},
    ],
)
@patch("limberframework.cache.lockers.Aioredlock")
def test_create_async_redis_locker(mock_aioredlock, connection):
    locker = AsyncRedisLocker(**connection)

    assert locker._locks == {}
    assert locker.lock_manager is mock_aioredlock.return_value

    if not connection["password"]:
        del connection["password"]

    mock_aioredlock.assert_called_once_with([connection], retry_count=1)


@mark.parametrize("key,expires_in", [("resource", 10), ("cache", 0)])
@mark.asyncio
async def test_async_redis_locker_lock(key, expires_in):
    mock_aioredlock = Mock()
    mock_aioredlock.lock = AsyncMock()

    locker = AsyncRedisLocker("localhost", 1234, 0, None)
    locker.lock_manager = mock_aioredlock

    await locker.lock(key, expires_in)

    mock_aioredlock.lock.assert_called_once_with(
        f"lock-{key}", lock_timeout=expires_in
    )
    assert locker._locks[key] == mock_aioredlock.lock.return_value


@patch("limberframework.cache.lockers.Aioredlock")
@mark.asyncio
async def test_async_redis_locker_unlock(mock_aioredlock):
    key = "resource"

    mock_aioredlock.return_value.unlock = AsyncMock()
    mock_lock = Mock()

    locker = AsyncRedisLocker("localhost", 1234, 0, None)
    locker._locks[key] = mock_lock

    await locker.unlock(key)

    mock_aioredlock.return_value.unlock.assert_called_once_with(mock_lock)


@patch("limberframework.cache.lockers.AsyncRedisLocker")
@mark.asyncio
async def test_make_locker(mock_asyncredislocker):
    config = {
        "locker": "asyncredis",
        "host": "localhost",
        "port": 1234,
        "db": 0,
        "password": None,
    }

    await make_locker(config)

    mock_asyncredislocker.assert_called_once_with(
        config["host"], config["port"], config["db"], config["password"]
    )


@mark.asyncio
async def test_make_locker_with_invalid_locker():
    config = {"locker": "test"}

    with raises(
        ValueError, match=f"Unsupported cache locker {config['locker']}."
    ):
        await make_locker(config)
