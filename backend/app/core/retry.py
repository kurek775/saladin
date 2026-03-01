"""Async retry utility with exponential backoff."""

import asyncio
import logging
from typing import Callable, TypeVar, Awaitable, Union, Tuple, List, Type
import importlib

from backend.app.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


# Default retryable exception types
RETRYABLE_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    OSError,
)


def _import_exceptions_from_strings(
    exception_strings: List[str]
) -> Tuple[Type[Exception], ...]:
    """Dynamically import exception classes from a list of fully qualified
    string names.
    """
    imported_exceptions = []
    for exc_str in exception_strings:
        try:
            module_name, class_name = exc_str.rsplit('.', 1)
            module = importlib.import_module(module_name)
            exc_class = getattr(module, class_name)
            if not issubclass(exc_class, Exception):
                logger.warning(
                    f"'{exc_str}' is not an Exception subclass. Skipping."
                )
                continue
            imported_exceptions.append(exc_class)
        except (ImportError, AttributeError) as e:
            logger.warning(
                f"Could not import exception '{exc_str}': {e}. Skipping."
            )
        except Exception as e:
            logger.error(
                f"Unexpected error importing exception '{exc_str}': {e}. "
                "Skipping."
            )
    return tuple(imported_exceptions)


async def with_retry(
    fn: Callable[..., Awaitable[T]],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable: Union[
        Tuple[Type[Exception], ...],
        List[str],
        None
    ] = None,
    **kwargs,
) -> T:
    """Execute an async function with exponential backoff retry.

    Args:
        fn: Async function to call.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay between retries.
        retryable: Tuple of exception types or list of fully qualified
                   exception names (strings) that trigger a retry.
                   If None, uses default and global settings.
    """
    # Start with default retryable exceptions
    all_retryable_exceptions: List[Type[Exception]] = \
        list(RETRYABLE_EXCEPTIONS)

    # Add globally configured retryable exceptions
    if settings.GLOBAL_RETRYABLE_EXCEPTIONS:
        global_exceptions = _import_exceptions_from_strings(
            settings.GLOBAL_RETRYABLE_EXCEPTIONS
        )
        all_retryable_exceptions.extend(global_exceptions)

    # Add or override with per-call retryable exceptions
    if retryable is not None:
        if isinstance(retryable, list):
            per_call_exceptions = _import_exceptions_from_strings(retryable)
            all_retryable_exceptions.extend(per_call_exceptions)
        elif isinstance(retryable, tuple):
            all_retryable_exceptions.extend(retryable)

    # Ensure unique exceptions and convert to tuple for exception handling
    final_retryable_exceptions = tuple(set(all_retryable_exceptions))
    if not final_retryable_exceptions:
        # If no retryable exceptions are configured, re-raise immediately
        logger.warning(
            "No retryable exceptions configured for with_retry. "
            "Function will not retry."
        )
        return await fn(*args, **kwargs)

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await fn(*args, **kwargs)
        except final_retryable_exceptions as e:
            last_error = e
            if attempt >= max_retries:
                logger.error(
                    "All %d retries exhausted for %s: %s",
                    max_retries, fn.__name__, e
                )
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            logger.warning(
                "Retry %d/%d for %s after %.1fs: %s",
                attempt + 1, max_retries, fn.__name__, delay, e,
            )
            await asyncio.sleep(delay)

    raise last_error  # Should not reach here
