"""Decorators focused on data operation error handling."""

import functools
import logging
from collections.abc import Callable
from typing import Any, TypeVar

import pandas as pd

from .decorators_base import ChinaDataError, logger

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


def handle_data_operation(
    operation_name: str,
    return_on_error: Any = None,
    log_level: int = logging.ERROR,
    reraise: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T | Any]]:
    """Decorator for consistent error handling in data operations."""

    def decorator(func: Callable[..., T]) -> Callable[..., T | Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T | Any:
            try:
                return func(*args, **kwargs)
            except ChinaDataError:
                raise
            except Exception as e:  # pylint: disable=broad-exception-caught
                if hasattr(logger, "bind"):
                    logger.exception(
                        "Error in %s",
                        operation_name,
                        operation=operation_name,
                        function=func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        args_preview=str(args)[:100],
                        kwargs_preview=str(kwargs)[:100],
                    )
                else:
                    logger.log(
                        log_level,
                        "Error in %s: %s",
                        operation_name,
                        str(e),
                        extra={
                            "operation": operation_name,
                            "function": func.__name__,
                            "function_args": str(args)[:100],
                            "function_kwargs": str(kwargs)[:100],
                        },
                    )
                if reraise:
                    raise
                return return_on_error

        return wrapper

    return decorator


def safe_dataframe_operation(
    operation_name: str,
    default_df: pd.DataFrame | None = None,
) -> Callable[[Callable[..., pd.DataFrame]], Callable[..., pd.DataFrame]]:
    """Decorator for DataFrame operations that should return an empty frame on error."""

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            try:
                result = func(*args, **kwargs)
                if isinstance(result, pd.DataFrame):
                    return result
                logger.warning(
                    "%s returned non-DataFrame result, converting to empty DataFrame",
                    operation_name,
                )
                return pd.DataFrame()
            except ChinaDataError:
                raise
            except Exception as e:  # pylint: disable=broad-exception-caught # noqa: BLE001
                logger.exception(
                    "Error in %s",
                    operation_name,
                    extra={
                        "operation": operation_name,
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                    },
                )
                return default_df if default_df is not None else pd.DataFrame()

        return wrapper

    return decorator
