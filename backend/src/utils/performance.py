"""Performance monitoring utilities."""

import asyncio
import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger(__name__)


def log_execution_time(operation_name: str):
    """
    Decorator to log execution time of functions.

    Usage:
        @log_execution_time("add_task_operation")
        def add_task(db, params):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    "Performance metric",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "success",
                    },
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "Performance metric",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "error",
                        "error": str(e),
                    },
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    "Performance metric",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "success",
                    },
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "Performance metric",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "error",
                        "error": str(e),
                    },
                )
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


@contextmanager
def track_performance(operation_name: str, user_id: str | None = None):
    """
    Context manager to track performance of code blocks.

    Usage:
        with track_performance("fetch_conversation_history", user_id="user-123"):
            messages = service.get_conversation_history(conv_id, user_id)
    """
    start_time = time.time()
    extra = {"operation": operation_name, "user_id": user_id}
    try:
        yield
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Performance metric",
            extra={**extra, "duration_ms": round(duration_ms, 2), "status": "success"},
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "Performance metric",
            extra={
                **extra,
                "duration_ms": round(duration_ms, 2),
                "status": "error",
                "error": str(e),
            },
        )
        raise
