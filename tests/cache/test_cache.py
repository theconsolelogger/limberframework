from datetime import datetime
from unittest.mock import MagicMock

from pytest import fixture, mark

from limberframework.cache.cache import Cache


@fixture
def mock_store():
    return MagicMock()


def test_load(mock_store):
    data = {"data": "test", "expires_at": datetime.now()}
    mock_store.__getitem__.return_value = data

    cache = Cache(mock_store)
    cache.load("test_cache")

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
def test_update(value, expires_at, updated, mock_store):
    mock_store.put.return_value = True
    key = "test_key"

    cache = Cache(mock_store)
    cache._key = key
    cache.value = value
    cache.expires_at = expires_at

    response = cache.update()

    assert response == updated
