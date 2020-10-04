from unittest.mock import AsyncMock, MagicMock, Mock, patch

from fastapi import Response
from pytest import mark

from limberframework.routing.exceptions import TooManyRequestsException
from limberframework.routing.middleware import ThrottleRequestMiddleware


def test_create_throttle_request_middleware():
    max_hits = 10
    decay = 30

    middleware = ThrottleRequestMiddleware(
        Mock(), max_hits=max_hits, decay=decay
    )

    assert middleware.max_hits == max_hits
    assert middleware.decay == decay


@mark.parametrize(
    "max_hits,remaining_hits,available_in,headers",
    [
        (
            20,
            10,
            1000,
            {
                "X-RateLimit-Limit": "20",
                "X-RateLimit-Remaining": "10",
                "X-RateLimit-Reset": "1000",
            },
        ),
        (
            40,
            20,
            None,
            {"X-RateLimit-Limit": "40", "X-RateLimit-Remaining": "20"},
        ),
    ],
)
def test_get_headers(max_hits, remaining_hits, available_in, headers):
    middleware = ThrottleRequestMiddleware(Mock())
    rate_limit_headers = middleware.get_headers(
        max_hits, remaining_hits, available_in
    )

    assert rate_limit_headers == headers


def test_add_headers():
    response = Response()
    max_hits = 25
    remaining_hits = 15
    available_in = 1500
    headers = {
        "X-RateLimit-Limit": str(max_hits),
        "X-RateLimit-Remaining": str(remaining_hits),
        "X-RateLimit-Reset": str(available_in),
    }

    middleware = ThrottleRequestMiddleware(Mock())
    middleware.get_headers = Mock(return_value=headers)
    response_headers = middleware.add_headers(
        response, max_hits, remaining_hits, available_in
    )

    for header in headers:
        response_headers.headers[header] == headers[header]


def test_request_signature():
    mock_request = Mock()
    mock_request.base_url = "http://test.com"
    mock_request.client.host = "127.0.0.1"

    middleware = ThrottleRequestMiddleware(Mock())
    request_signature = middleware.request_signature(mock_request)

    assert request_signature == "78cf3b452b5a215553d2f70ffd8d6832eb7d651b"


@mark.asyncio
@patch(
    "limberframework.routing.middleware.make_rate_limiter",
    new_callable=AsyncMock,
)
async def test_dispatch_too_many_requests_exception(mock_make_rate_limiter):
    max_hits = 10
    remaining_hits = 0
    available_in = 1000
    headers = {
        "X-RateLimit-Limit": str(max_hits),
        "X-RateLimit-Remaining": str(remaining_hits),
        "X-RateLimit-Reset": str(available_in),
    }

    mock_rate_limiter = Mock()
    mock_rate_limiter.hit = AsyncMock(side_effect=TooManyRequestsException)
    mock_rate_limiter.max_hits = max_hits
    mock_rate_limiter.remaining_hits.return_value = remaining_hits
    mock_rate_limiter.available_in.return_value = available_in

    mock_make_rate_limiter.return_value = mock_rate_limiter

    mock_request = MagicMock()
    mock_request.app.make = AsyncMock()

    middleware = ThrottleRequestMiddleware(Mock())
    response = await middleware.dispatch(mock_request, AsyncMock())

    for header in headers:
        response.headers[header] == headers[header]

    assert response.status_code == 429


@mark.asyncio
@patch(
    "limberframework.routing.middleware.make_rate_limiter",
    new_callable=AsyncMock,
)
async def test_dispatch(mock_make_rate_limiter):
    max_hits = 10
    remaining_hits = 0
    available_in = 1000
    headers = {
        "X-RateLimit-Limit": str(max_hits),
        "X-RateLimit-Remaining": str(remaining_hits),
        "X-RateLimit-Reset": str(available_in),
    }

    mock_rate_limiter = Mock()
    mock_rate_limiter.hit = AsyncMock()
    mock_rate_limiter.max_hits = max_hits
    mock_rate_limiter.remaining_hits.return_value = remaining_hits
    mock_rate_limiter.available_in.return_value = available_in

    mock_make_rate_limiter.return_value = mock_rate_limiter

    mock_request = MagicMock()
    mock_request.app.make = AsyncMock()

    mock_call_next = AsyncMock()
    mock_call_next.return_value = Response()

    middleware = ThrottleRequestMiddleware(Mock())
    response = await middleware.dispatch(mock_request, mock_call_next)

    for header in headers:
        response.headers[header] == headers[header]

    assert response.status_code == 200
