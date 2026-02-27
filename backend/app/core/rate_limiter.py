"""Async rate limiter using leaky bucket algorithm."""

import asyncio
import hashlib
import logging
import time

from app.config import settings

logger = logging.getLogger(__name__)


class LeakyBucket:
    """Async leaky bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        """
        Args:
            rate: Tokens per second to leak (refill rate).
            capacity: Maximum burst capacity.
        """
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a token is available."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_time
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._last_time = now

            if self._tokens >= 1:
                self._tokens -= 1
                return

            # Wait for a token
            wait_time = (1 - self._tokens) / self.rate
            await asyncio.sleep(wait_time)
            self._tokens = 0
            self._last_time = time.monotonic()


class RateLimiterRegistry:
    """Per-key rate limiter buckets.

    Key format: "provider:api_key_hash[:8]"
    """

    def __init__(self):
        self._buckets: dict[str, LeakyBucket] = {}

    def _bucket_key(self, provider: str, api_key: str) -> str:
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:8] if api_key else "default"
        return f"{provider}:{key_hash}"

    def get_bucket(self, provider: str, api_key: str = "") -> LeakyBucket:
        key = self._bucket_key(provider, api_key)
        if key not in self._buckets:
            rpm = settings.RATE_LIMIT_RPM
            rate = rpm / 60.0  # Convert RPM to tokens per second
            self._buckets[key] = LeakyBucket(rate=rate, capacity=max(5, rpm // 10))
        return self._buckets[key]

    async def acquire(self, provider: str, api_key: str = "") -> None:
        bucket = self.get_bucket(provider, api_key)
        await bucket.acquire()


# Singleton
rate_limiter = RateLimiterRegistry()
