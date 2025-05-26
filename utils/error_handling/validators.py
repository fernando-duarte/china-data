"""Validation utilities for China data processing.

This module provides validation functions and error logging utilities
for data quality assurance.
"""

import logging
from typing import Any

import pandas as pd

from .exceptions import DataValidationError

logger = logging.getLogger(__name__)


def log_error_with_context(
    logger_instance: logging.Logger,
    message: str,
    error: Exception,
    context: dict[str, Any] | None = None,
    level: int = logging.ERROR,
) -> None:
    """Log an error with additional context information.

    Args:
        logger_instance: Logger to use
        message: Base error message
        error: The exception that occurred
        context: Additional context information
        level: Logging level
    """
    error_info = {"error_type": type(error).__name__, "error_message": str(error), "original_message": message}

    if context:
        error_info.update(context)

    logger_instance.log(level, "%s: %s", message, str(error), extra=error_info)


def validate_dataframe_not_empty(df: pd.DataFrame, name: str) -> None:
    """Validate that a DataFrame is not empty.

    Args:
        df: DataFrame to validate
        name: Name of the DataFrame for error messages

    Raises:
        DataValidationError: If DataFrame is empty
    """
    if len(df) == 0:
        raise DataValidationError(
            column=name, message="DataFrame is empty", data_info=f"Shape: {df.shape}, Columns: {list(df.columns)}"
        )


def validate_required_columns(df: pd.DataFrame, required_columns: list[str], name: str) -> None:
    """Validate that a DataFrame contains required columns.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        name: Name of the DataFrame for error messages

    Raises:
        DataValidationError: If required columns are missing
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise DataValidationError(
            column=name,
            message=f"Missing required columns: {missing_columns}",
            data_info=f"Available columns: {list(df.columns)}",
        )


def _raise_conversion_error(column_name: str, series: "pd.Series[str | float]") -> None:
    """Raise a DataValidationError for failed numeric conversion."""
    raise DataValidationError(
        column=column_name,
        message="All values failed numeric conversion",
        data_info=f"Sample values: {series.head().tolist()}",
    )


def safe_numeric_conversion(series: "pd.Series[str | float]", column_name: str) -> "pd.Series[float]":
    """Safely convert a pandas Series to numeric, with error handling.

    Args:
        series: Series to convert
        column_name: Name of the column for error messages

    Returns:
        Converted series with numeric values

    Raises:
        DataValidationError: If conversion fails completely
    """
    try:
        converted = pd.to_numeric(series, errors="coerce")

        # Check if all values became NaN
        if converted.isna().all() and not series.isna().all():
            _raise_conversion_error(column_name, series)

        # Log warning if some values failed conversion
        failed_count = converted.isna().sum() - series.isna().sum()
        if failed_count > 0:
            logger.warning(
                "Failed to convert %d values to numeric in column %s",
                failed_count,
                column_name,
                extra={"column": column_name, "failed_count": failed_count},
            )

    except Exception as e:
        raise DataValidationError(
            column=column_name,
            message=f"Numeric conversion failed: {e!s}",
            data_info=f"Series dtype: {series.dtype}, length: {len(series)}",
        ) from e

    return converted
