"""Error handling decorators for China data processing.

This module provides decorators for consistent error handling patterns
across the data processing pipeline.
"""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar, cast

import pandas as pd

from .exceptions import ChinaDataError

try:
    from utils.logging_config import get_logger

    # Use get_logger for consistency
    logger = get_logger(__name__)
except ImportError:
    # Fallback to standard logging if structured logging is not available
    logger = logging.getLogger(__name__)

# Type variable for generic return types
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


def handle_data_operation(
    operation_name: str, return_on_error: Any = None, log_level: int = logging.ERROR, reraise: bool = False
) -> Callable[[Callable[..., T]], Callable[..., T | Any]]:
    """Decorator for consistent error handling in data operations.

    Args:
        operation_name: Name of the operation for logging
        return_on_error: Value to return on error (default: None)
        log_level: Logging level for errors
        reraise: Whether to reraise the exception after logging

    Returns:
        Decorated function with error handling
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T | Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T | Any:
            try:
                return func(*args, **kwargs)
            except ChinaDataError:
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Use structured logging if available, otherwise fall back to standard logging
                if hasattr(logger, "bind"):
                    # Structured logging
                    logger.exception(
                        "Error in %s",
                        operation_name,
                        operation=operation_name,
                        function=func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        args_preview=str(args)[:100],  # Truncate long args
                        kwargs_preview=str(kwargs)[:100],
                    )
                else:
                    # Standard logging
                    logger.log(
                        log_level,
                        "Error in %s: %s",
                        operation_name,
                        str(e),
                        extra={
                            "operation": operation_name,
                            "function": func.__name__,
                            "function_args": str(args)[:100],  # Truncate long args
                            "function_kwargs": str(kwargs)[:100],
                        },
                    )
                if reraise:
                    raise
                return return_on_error

        return wrapper

    return decorator


def safe_dataframe_operation(
    operation_name: str, default_df: pd.DataFrame | None = None
) -> Callable[[Callable[..., pd.DataFrame]], Callable[..., pd.DataFrame]]:
    """Decorator specifically for DataFrame operations that should return empty DataFrame on error.

    Args:
        operation_name: Name of the operation for logging
        default_df: Default DataFrame to return on error (if None, returns empty DataFrame)

    Returns:
        Decorated function that returns DataFrame on success or default on error
    """

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            try:
                result = func(*args, **kwargs)
                if isinstance(result, pd.DataFrame):
                    return result
                logger.warning("%s returned non-DataFrame result, converting to empty DataFrame", operation_name)
                return pd.DataFrame()
            except ChinaDataError:
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                logger.exception(
                    "Error in %s",
                    operation_name,
                    extra={"operation": operation_name, "function": func.__name__, "error_type": type(e).__name__},
                )
                return default_df if default_df is not None else pd.DataFrame()

        return wrapper

    return decorator


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
                            # Structured logging
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
                            # Standard logging
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
                            # Structured logging
                            logger.exception(
                                "%s after %d attempts",
                                error_message,
                                max_attempts,
                                max_attempts=max_attempts,
                                error_type=type(e).__name__,
                                error_message=str(e),
                            )
                        else:
                            # Standard logging
                            logger.exception("%s after %d attempts", error_message, max_attempts)
                        raise
            # This should never be reached due to the logic above, but mypy needs it
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
            # Structured logging
            logger.info(
                "Function execution completed", function=func.__name__, duration_seconds=round(end_time - start_time, 3)
            )
        else:
            # Standard logging
            logger.info("%s took %.2f seconds to execute", func.__name__, end_time - start_time)
        return result

    return cast("F", wrapper)
