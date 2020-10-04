"""Exceptions

Classes:
CacheLockError: Error occurred when locking the cache.
"""


class CacheLockError(Exception):
    """An exception for when an error occurs when
    when locking a resource in the store.
    """

    def __init__(self, message: str) -> None:
        """Establish the message of the exception.

        Arguments:
        message str -- the exception message.
        """
        super().__init__(message)
