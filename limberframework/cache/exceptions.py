"""Exceptions related to the cache."""


class CacheLockError(Exception):
    """An error occured when locking a resource in the store."""

    def __init__(self, message: str) -> None:
        """Establish the message of the exception.

        Args:
            message: The exception message.
        """
        super().__init__(message)
