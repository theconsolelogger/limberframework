from datetime import datetime
from unittest.mock import AsyncMock

from pytest import fixture, mark

from limberframework.cache.cache import Cache


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
