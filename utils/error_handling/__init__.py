"""
Centralized error handling utilities for the China data processor.

This package provides consistent error handling patterns, custom exceptions,
and utilities for error context preservation.
"""

from .decorators import handle_data_operation, safe_dataframe_operation
from .exceptions import (
    ChinaDataError,
    DataDownloadError,
    DataValidationError,
    FileOperationError,
    ProjectionError,
)
from .validators import (
    log_error_with_context,
    safe_numeric_conversion,
    validate_dataframe_not_empty,
    validate_required_columns,
)

__all__ = [
    "ChinaDataError",
    "DataDownloadError",
    "DataValidationError",
    "ProjectionError",
    "FileOperationError",
    "handle_data_operation",
    "safe_dataframe_operation",
    "log_error_with_context",
    "validate_dataframe_not_empty",
    "validate_required_columns",
    "safe_numeric_conversion",
]
