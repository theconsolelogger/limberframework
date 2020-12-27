"""Exceptions relating to routing requests."""
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class TooManyRequestsException(Exception):
    """An exception for when a client reaches the rate limit.

    Attributes:
        status_code: A HTTP status code.
        detail: Message to describe the error.
    """

    def __init__(
        self,
        status_code: int = HTTP_429_TOO_MANY_REQUESTS,
        detail: str = "Too many requests.",
    ) -> None:
        """Establish the status code and detail.

        Args:
            status_code: A HTTP status code.
            detail: Message to describe the error.
        """
        self.status_code = status_code
        self.detail = detail

        super().__init__()
