"""Retry utilities for handling transient failures."""

import logging
import time
from functools import wraps
from typing import Callable, TypeVar, Any
from sqlalchemy.exc import OperationalError, DBAPIError

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_on_db_error(
    max_attempts: int = 3,
    initial_delay: float = 0.1,
    backoff_factor: float = 2.0
):
    """
    Decorator to retry database operations on transient failures.

    Uses exponential backoff: 0.1s, 0.2s, 0.4s, etc.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 0.1)
        backoff_factor: Multiplier for delay after each attempt (default: 2.0)

    Usage:
        @retry_on_db_error(max_attempts=3)
        def create_task(db, params):
            ...

    Example with Exponential Backoff:
        Attempt 1 fails → Wait 0.1s → Attempt 2
        Attempt 2 fails → Wait 0.2s → Attempt 3
        Attempt 3 fails → Raise exception
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DBAPIError) as e:
                    last_exception = e
                    error_msg = str(e)

                    # Check if this is a transient error worth retrying
                    is_transient = any(
                        keyword in error_msg.lower()
                        for keyword in [
                            "connection",
                            "timeout",
                            "server closed",
                            "lost connection",
                        ]
                    )

                    if attempt < max_attempts and is_transient:
                        logger.warning(
                            f"Database operation failed (attempt {attempt}/{max_attempts}), "
                            f"retrying in {delay}s",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "max_attempts": max_attempts,
                                "delay_seconds": delay,
                                "error": error_msg,
                            },
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"Database operation failed after {attempt} attempts",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "error": error_msg,
                            },
                            exc_info=True,
                        )
                        raise

            # Should never reach here, but just in case
            raise last_exception

        return wrapper

    return decorator
