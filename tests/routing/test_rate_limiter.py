from datetime import datetime, timedelta
from math import ceil
from unittest.mock import patch

from pytest import mark, raises

from limberframework.routing.exceptions import TooManyRequestsException
from limberframework.routing.rate_limiter import RateLimiter


@patch("limberframework.routing.rate_limiter.Cache")
@mark.parametrize("value,hits", [(10, 10), (None, 0)])
def test_get_hits(mock_cache, value, hits):
    mock_cache.value = value

    rate_limiter = RateLimiter(mock_cache, "test", 60, 60)
    response = rate_limiter.get_hits()

    assert response == hits


@patch("limberframework.routing.rate_limiter.Cache")
def test_set_hits(mock_cache):
    hits = 10
    date = datetime.now()
    mock_cache.expires_at = date

    rate_limiter = RateLimiter(mock_cache, "test", 60, 60)
    rate_limiter.set_hits(hits)

    assert mock_cache.value == str(hits)
    mock_cache.update.assert_called_once()


@patch("limberframework.routing.rate_limiter.Cache")
def test_set_hits_no_expiry(mock_cache):
    hits = 10
    mock_cache.expires_at = None

    rate_limiter = RateLimiter(mock_cache, "test", 60, 60)
    rate_limiter.set_hits(hits)

    assert mock_cache.value == str(hits)
    assert mock_cache.expires_at is not None
    mock_cache.update.assert_called_once()


@patch("limberframework.routing.rate_limiter.Cache")
def test_remaining_hits(mock_cache):
    max_hits = 60
    hits = 20
    mock_cache.value = hits

    rate_limiter = RateLimiter(mock_cache, "test", max_hits, 60)
    response = rate_limiter.remaining_hits()

    assert response == (max_hits - hits)


@patch("limberframework.routing.rate_limiter.datetime")
@patch("limberframework.routing.rate_limiter.Cache")
def test_available_in(mock_cache, mock_date_time):
    decay = 60
    now = datetime.now()
    mock_date_time.now.return_value = now
    mock_cache.expires_at = None

    rate_limiter = RateLimiter(mock_cache, "test", 60, decay)
    response = rate_limiter.available_in()

    assert response == ceil((now + timedelta(seconds=decay)).timestamp())


@patch("limberframework.routing.rate_limiter.datetime")
@patch("limberframework.routing.rate_limiter.Cache")
def test_available_in_no_expiry(mock_cache, mock_date_time):
    decay = 60
    now = datetime.now()
    expiry = datetime.now() + timedelta(seconds=120)
    mock_date_time.now.return_value = now
    mock_cache.expires_at = expiry

    rate_limiter = RateLimiter(mock_cache, "test", 60, decay)
    response = rate_limiter.available_in()

    assert response == ceil((expiry - now).total_seconds())


@patch("limberframework.routing.rate_limiter.Cache")
def test_hit_exception(mock_cache):
    hits = 60
    mock_cache.value = hits

    rate_limiter = RateLimiter(mock_cache, "test", hits, 60)

    with raises(TooManyRequestsException):
        rate_limiter.hit()


@patch("limberframework.routing.rate_limiter.Cache")
def test_hit(mock_cache):
    hits = 40
    mock_cache.value = hits

    rate_limiter = RateLimiter(mock_cache, "test", 60, 60)
    rate_limiter.hit()

    assert mock_cache.value == str(hits + 1)
