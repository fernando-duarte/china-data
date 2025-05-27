"""Decorators providing retry logic and execution time logging."""

import functools
import time
from typing import Any, cast

from .decorators_base import F, logger


def retry_on_exception(
    max_attempts: int = 3,
    delay: int = 5,
    allowed_exceptions: tuple[type[BaseException], ...] = (Exception,),
    error_message: str = "Unexpected error",
) -> Callable[[F], F]:
    """Decorator to retry a function on exception."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempts in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    if attempts < max_attempts - 1:
                        if hasattr(logger, "bind"):
                            logger.warning(
                                "%s on attempt %d, retrying",
                                error_message,
                                attempts + 1,
                                attempt=attempts + 1,
                                max_attempts=max_attempts,
                                delay_seconds=delay,
                                error_type=type(e).__name__,
                                error_message=str(e),
                            )
                        else:
                            logger.warning(
                                "%s on attempt %d, retrying in %d seconds: %s",
                                error_message,
                                attempts + 1,
                                delay,
                                str(e),
                            )
                        time.sleep(delay)
                    else:
                        if hasattr(logger, "bind"):
                            logger.exception(
                                "%s after %d attempts",
                                error_message,
                                max_attempts,
                                max_attempts=max_attempts,
                                error_type=type(e).__name__,
                                error_message=str(e),
                            )
                        else:
                            logger.exception(
                                "%s after %d attempts",
                                error_message,
                                max_attempts,
                            )
                        raise
            error_msg = f"Unexpected exit from retry loop after {max_attempts} attempts"
            raise RuntimeError(error_msg)

        return cast("F", wrapper)

    return decorator


def log_execution_time(func: F) -> F:
    """Decorator to log function execution time."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        if hasattr(logger, "bind"):
            logger.info(
                "Function execution completed",
                function=func.__name__,
                duration_seconds=round(end_time - start_time, 3),
            )
        else:
            logger.info("%s took %.2f seconds to execute", func.__name__, end_time - start_time)
        return result

    return cast("F", wrapper)

