"""Handles rate limiting requests."""
from datetime import datetime, timedelta
from math import ceil

from limberframework.cache.cache import Cache
from limberframework.routing.exceptions import TooManyRequestsException


class RateLimiter:
    """Handle storing and retrieving rate limit information in the cache.

    Attributes:
        cache: Store object that is acting as the cache.
        max_hits: Number of allowed requests.
        decay: Number of seconds when hits are refreshed.
    """

    def __init__(
        self, cache: Cache, key: str, max_hits: int, decay: int
    ) -> None:
        """Set up the rate limiter.

        Args:
            cache: Cache object.
            key: Identifier for the client.
            max_hits: Number of allowed requests.
            decay: Number of seconds when hits are refreshed.
        """
        self.cache: Cache = cache
        self.max_hits: int = max_hits
        self.decay: int = decay

    def get_hits(self) -> int:
        """Retrieve number of hits for a request from the cache.

        Returns:
            int: The number of hits.
        """
        if not self.cache.value:
            return 0
        return int(self.cache.value)

    async def set_hits(self, number_hits: int) -> None:
        """Update the store with the number of hits.

        Additionally update the expiry time if not
        already updated.

        Args:
            number_hits: Value of hits to store.
        """
        self.cache.value = str(number_hits)

        if not self.cache.expires_at:
            self.cache.expires_at = datetime.now() + timedelta(
                seconds=self.decay
            )

        await self.cache.update()

    async def hit(self) -> None:
        """Update cache with new record for a request."""
        number_hits = self.get_hits()

        if number_hits >= self.max_hits:
            raise TooManyRequestsException()

        await self.set_hits(number_hits + 1)

    def available_in(self) -> int:
        """Calculate number of seconds until the available hits is refreshed.

        Returns:
            int: Number of seconds.
        """
        if not self.cache.expires_at:
            return ceil(
                (datetime.now() + timedelta(seconds=self.decay)).timestamp()
            )
        return ceil((self.cache.expires_at - datetime.now()).total_seconds())

    def remaining_hits(self) -> int:
        """Calculate the number of hits available.

        Returns:
            int: Number of remaining hits.
        """
        return self.max_hits - self.get_hits()


async def make_rate_limiter(
    cache: Cache, key: str, max_hits: int, decay: int
) -> RateLimiter:
    """Create a rate limiter.

    Args:
        cache: Cache to use to store rate limit data.
        key: Identifier for the client.
        max_hits: Number of allowed hits.
        decay: Number of seconds when hits are refreshed.

    Returns:
        RateLimiter: The created rate limiter.
    """
    await cache.load(key)
    return RateLimiter(cache, key, max_hits, decay)
