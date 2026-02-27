"""Async retry utility with exponential backoff."""

import asyncio
import logging
from typing import Callable, TypeVar, Awaitable

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Default retryable exception types
RETRYABLE_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    OSError,
)


async def with_retry(
    fn: Callable[..., Awaitable[T]],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable: tuple[type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    **kwargs,
) -> T:
    """Execute an async function with exponential backoff retry.

    Args:
        fn: Async function to call.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay between retries.
        retryable: Tuple of exception types that trigger a retry.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await fn(*args, **kwargs)
        except retryable as e:
            last_error = e
            if attempt >= max_retries:
                logger.error("All %d retries exhausted for %s: %s", max_retries, fn.__name__, e)
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            logger.warning(
                "Retry %d/%d for %s after %.1fs: %s",
                attempt + 1, max_retries, fn.__name__, delay, e,
            )
            await asyncio.sleep(delay)

    raise last_error  # Should not reach here
