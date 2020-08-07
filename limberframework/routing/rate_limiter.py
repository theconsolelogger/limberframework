"""Rate Limiter

Classes:
- RateLimiter: handles rate limiting requests.
"""
from datetime import datetime, timedelta
from math import ceil
from limberframework.cache.cache import Cache
from limberframework.routing.exceptions import TooManyRequestsException

class RateLimiter:
    """Handles storing and retrieving information in the cache
    that is helpful in rate limiting requests.

    Attributes:
    cache Store -- Store object that is acting as the cache.
    max_hits int -- number of allowed requests.
    decay int -- number of seconds when hits are refreshed.
    """
    def __init__(self, cache: Cache, key: str, max_hits: int, decay: int) -> None:
        """Sets up the rate limiter.

        Arguments:
        cache Cache -- Cache object.
        key str -- identifier for the client.
        max_hits int -- number of allowed requests.
        decay int -- number of seconds when hits are refreshed.
        """
        self.cache: Cache = cache
        self.max_hits: int = max_hits
        self.decay: int = decay

        cache.load(key)

    def get_hits(self) -> int:
        """Retrieves number of hits for a request
        from the cache.

        Returns int.
        """
        if not self.cache.value:
            return 0
        return int(self.cache.value)

    def set_hits(self, number_hits: int) -> None:
        """Updates the store with the number of hits,
        additionally updates the expiry time if not
        already updated.

        Arguments:
        number_hits int -- value of hits to store.
        """
        self.cache.value = str(number_hits)

        if not self.cache.expires_at:
            self.cache.expires_at = datetime.now() + timedelta(seconds=self.decay)

        self.cache.update()

    def hit(self) -> None:
        """Update cache with new record for a request."""
        number_hits = self.get_hits()

        if number_hits >= self.max_hits:
            raise TooManyRequestsException()

        self.set_hits(number_hits + 1)

    def available_in(self) -> int:
        """Calculates the number of seconds until
        the available hits is refreshed.

        Returns int.
        """
        if not self.cache.expires_at:
            return ceil((datetime.now() + timedelta(seconds=self.decay)).timestamp())
        return ceil((self.cache.expires_at - datetime.now()).total_seconds())

    def remaining_hits(self) -> int:
        """Calculates the number of hits available.

        Returns int.
        """
        return self.max_hits - self.get_hits()
