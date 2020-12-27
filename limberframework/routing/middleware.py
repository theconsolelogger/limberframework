"""Middleware relating to routing requests."""
from typing import Dict

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from limberframework.hashing.hashers import Hasher
from limberframework.routing.exceptions import TooManyRequestsException
from limberframework.routing.rate_limiter import make_rate_limiter


class ThrottleRequestMiddleware(BaseHTTPMiddleware):
    """Enforces rate limits on clients sending requests to the API.

    Attributes:
        max_hits: Number of allowed requests by a client.
        decay: Number of seconds the max_hits applies for.
    """

    def __init__(
        self, *args, max_hits: int = 60, decay: int = 60, **kwargs
    ) -> None:
        """Establish the middleware.

        Args:
            max_hits: Number of allowed requests by a client.
            decay: Number of seconds the max_hits applies for.
        """
        self.max_hits = max_hits
        self.decay = decay

        super().__init__(*args, **kwargs)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Check a request against the rate limit.

        Checks that a request is within the rate limit before processing.
        If within the limit, the number of hits is updated.
        Otherwise the request is terminated.
        Additionally, rate limit information is added to the response.

        Args:
            request: The inbound request from a client.
            call_next: The next callable to continue processing the request.

        Returns:
            Response: Response to the client request.
        """
        response = Response("Internal server error", status_code=500)

        key = self.request_signature(request)
        cache = await request.app.make("cache")
        limiter = await make_rate_limiter(
            cache, key, self.max_hits, self.decay
        )

        try:
            await limiter.hit()
            response = await call_next(request)
        except TooManyRequestsException as error:
            response = Response(error.detail, error.status_code)
        finally:
            self.add_headers(
                response,
                limiter.max_hits,
                limiter.remaining_hits(),
                limiter.available_in(),
            )

        return response

    def request_signature(self, request: Request) -> str:
        """Generate a unique identifier for the client.

        Uses the SHA1 algorithm to generate the identifier.

        Args:
            request: A Request object.

        Returns:
            str: The unique identifier for the client.
        """
        key = str(request.base_url) + "|" + str(request.client.host)
        hasher = Hasher("sha1")
        return hasher(key)

    def add_headers(
        self,
        response: Response,
        max_hits: int,
        remaining_hits: int,
        available_in: int,
    ) -> Response:
        """Add rate limit headers to HTTP response.

        Args:
            response: A Response object.
            max_hits: Number of allowed requests by a client.
            remaining_hits: Number of unused allowed requests by a client.
            available_in: Number of seconds until the number
                of allowed requests is refreshed.

        Returns:
            Response: Response to the client request.
        """
        headers = self.get_headers(max_hits, remaining_hits, available_in)

        for header, value in headers.items():
            response.headers[header] = value

        return response

    def get_headers(
        self, max_hits: int, remaining_hits: int, available_in: int = None
    ) -> Dict:
        """Generate rate limit headers.

        Args:
            max_hits: Number of allowed requests by a client.
            remaining_hits: Number of unused allowed requests by a client.
            available_in: Number of seconds until the number
                of allowed requests is refreshed.

        Returns:
            dict: Dictionary containing the rate limit headers.
        """
        headers = {
            "X-RateLimit-Limit": str(max_hits),
            "X-RateLimit-Remaining": str(remaining_hits),
        }

        if available_in:
            headers["X-RateLimit-Reset"] = str(available_in)

        return headers
