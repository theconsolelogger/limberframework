"""Middleware

Middleware relating to routing requests.

Classes:
- ThrottleRequestMiddleware: Enforces rate limits on clients.
"""
from typing import Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from limberframework.hashing.hashers import Hasher
from limberframework.routing.exceptions import TooManyRequestsException
from limberframework.routing.rate_limiter import RateLimiter

class ThrottleRequestMiddleware(BaseHTTPMiddleware):
    """Enforces rate limits on clients sending requests to the API.

    Attributes:
    max_hits int -- number of allowed requests by a client.
    decay int -- number of seconds the max_hits applies for.
    """
    def __init__(self, *args, max_hits: int = 60, decay: int = 60, **kwargs) -> None:
        """Establishes the middleware.

        Arguments:
        max_hits int -- number of allowed requests by a client.
        decay int -- number of seconds the max_hits applies for.
        """
        self.max_hits = max_hits
        self.decay = decay

        super().__init__(*args, **kwargs)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = Response("Internal server error", status_code=500)

        key = self.request_signature(request)
        limiter = RateLimiter(request.app['cache'], key, self.max_hits, self.decay)

        try:
            limiter.hit()
            response = await call_next(request)
        except TooManyRequestsException as error:
            response = Response(
                error.detail,
                error.status_code
            )
        finally:
            self.add_headers(
                response,
                limiter.max_hits,
                limiter.remaining_hits(),
                limiter.available_in()
            )

        return response

    def request_signature(self, request: Request) -> str:
        """Generates a unique identifier for
        the client using the SHA1 algorithm.

        Arguments:
        request Request -- a Request object.

        Returns str.
        """
        key = str(request.base_url) + '|' + str(request.client.host)
        hasher = Hasher('sha1')
        return hasher.hash(key)

    def add_headers(
        self,
        response: Response,
        max_hits: int,
        remaining_hits: int,
        available_in: int
    ) -> Response:
        """Adds rate limit headers to HTTP response.

        Arguments:
        response Response -- a Response object.
        max_hits int -- number of allowed requests by a client.
        remaining_hits int --  number of unused allowed requests by a client.
        available_in int -- number of seconds until the number of allowed requests is refreshed.

        Returns Response.
        """
        headers = self.get_headers(max_hits, remaining_hits, available_in)

        for header, value in headers.items():
            response.headers[header] = value

        return response

    def get_headers(self, max_hits: int, remaining_hits: int, available_in: int = None) -> Dict:
        """Generates rate limit headers.

        Arguments:
        max_hits int -- number of allowed requests by a client.
        remaining_hits int --  number of unused allowed requests by a client.
        available_in int -- number of seconds until the number of allowed requests is refreshed.

        Returns dict.
        """
        headers = {
            'X-RateLimit-Limit': str(max_hits),
            'X-RateLimit-Remaining': str(remaining_hits)
        }

        if available_in:
            headers['X-RateLimit-Reset'] = str(available_in)

        return headers
