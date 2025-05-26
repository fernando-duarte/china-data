"""Centralized error handling utilities for the China data processor.

This package provides consistent error handling patterns, custom exceptions,
and utilities for error context preservation.
"""

import logging
import sys
from typing import Any, NoReturn

from .decorators import handle_data_operation, safe_dataframe_operation
from .exceptions import ChinaDataError, DataDownloadError, DataValidationError, FileOperationError, ProjectionError
from .validators import (
    log_error_with_context,
    safe_numeric_conversion,
    validate_dataframe_not_empty,
    validate_required_columns,
)


def setup_error_handling() -> None:
    """Configure logging for error handling."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s:%(filename)s:%(lineno)d %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("error.log")],
    )


def log_and_raise(error_msg: str, exception_class: type = Exception, **kwargs: Any) -> NoReturn:
    """Log an error message and raise an exception."""
    logger = logging.getLogger(__name__)
    logger.error(error_msg, **kwargs)
    raise exception_class(error_msg)


__all__ = [
    "ChinaDataError",
    "DataDownloadError",
    "DataValidationError",
    "FileOperationError",
    "ProjectionError",
    "handle_data_operation",
    "log_error_with_context",
    "safe_dataframe_operation",
    "safe_numeric_conversion",
    "validate_dataframe_not_empty",
    "validate_required_columns",
]
