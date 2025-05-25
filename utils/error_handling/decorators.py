"""
Error handling decorators for China data processing.

This module provides decorators for consistent error handling patterns
across the data processing pipeline.
"""

import functools
import logging
from typing import Any, Callable, Optional, TypeVar, Union

import pandas as pd

from .exceptions import ChinaDataError

logger = logging.getLogger(__name__)

# Type variable for generic return types
T = TypeVar("T")


def handle_data_operation(
    operation_name: str, return_on_error: Any = None, log_level: int = logging.ERROR, reraise: bool = False
) -> Callable:
    """
    Decorator for consistent error handling in data operations.

    Args:
        operation_name: Name of the operation for logging
        return_on_error: Value to return on error (default: None)
        log_level: Logging level for errors
        reraise: Whether to reraise the exception after logging

    Returns:
        Decorated function with error handling
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, Any]:
            try:
                return func(*args, **kwargs)
            except ChinaDataError:
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                logger.log(
                    log_level,
                    f"Error in {operation_name}: {str(e)}",
                    extra={
                        "operation": operation_name,
                        "function": func.__name__,
                        "args": str(args)[:100],  # Truncate long args
                        "kwargs": str(kwargs)[:100],
                    },
                )
                if reraise:
                    raise
                return return_on_error

        return wrapper

    return decorator


def safe_dataframe_operation(operation_name: str, default_df: Optional[pd.DataFrame] = None) -> Callable:
    """
    Decorator specifically for DataFrame operations that should return empty DataFrame on error.

    Args:
        operation_name: Name of the operation for logging
        default_df: Default DataFrame to return on error (if None, returns empty DataFrame)

    Returns:
        Decorated function that returns DataFrame on success or default on error
    """

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> pd.DataFrame:
            try:
                result = func(*args, **kwargs)
                if not isinstance(result, pd.DataFrame):
                    logger.warning(f"{operation_name} returned non-DataFrame result, converting to empty DataFrame")
                    return pd.DataFrame()
                return result
            except ChinaDataError:
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                logger.error(
                    f"Error in {operation_name}: {str(e)}",
                    extra={"operation": operation_name, "function": func.__name__, "error_type": type(e).__name__},
                )
                return default_df if default_df is not None else pd.DataFrame()

        return wrapper

    return decorator
