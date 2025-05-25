"""
Centralized error handling utilities for the China data processor.

This module provides consistent error handling patterns, custom exceptions,
and utilities for error context preservation.
"""

import logging
from typing import Any, Callable, Optional, TypeVar, Union
import pandas as pd
import functools

logger = logging.getLogger(__name__)

# Type variable for generic return types
T = TypeVar('T')


class ChinaDataError(Exception):
    """Base exception for China data processing errors."""
    pass


class DataDownloadError(ChinaDataError):
    """Raised when data download fails."""
    def __init__(self, source: str, indicator: str, message: str, original_error: Optional[Exception] = None):
        self.source = source
        self.indicator = indicator
        self.original_error = original_error
        super().__init__(f"Failed to download {indicator} from {source}: {message}")


class DataValidationError(ChinaDataError):
    """Raised when data validation fails."""
    def __init__(self, column: str, message: str, data_info: Optional[str] = None):
        self.column = column
        self.data_info = data_info
        super().__init__(f"Data validation failed for {column}: {message}")


class ProjectionError(ChinaDataError):
    """Raised when data projection/extrapolation fails."""
    def __init__(self, method: str, column: str, message: str, original_error: Optional[Exception] = None):
        self.method = method
        self.column = column
        self.original_error = original_error
        super().__init__(f"Projection failed for {column} using {method}: {message}")


class FileOperationError(ChinaDataError):
    """Raised when file operations fail."""
    def __init__(self, operation: str, filepath: str, message: str, original_error: Optional[Exception] = None):
        self.operation = operation
        self.filepath = filepath
        self.original_error = original_error
        super().__init__(f"File {operation} failed for {filepath}: {message}")


def handle_data_operation(
    operation_name: str,
    return_on_error: Any = None,
    log_level: int = logging.ERROR,
    reraise: bool = False
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
                        'operation': operation_name,
                        'function': func.__name__,
                        'args': str(args)[:100],  # Truncate long args
                        'kwargs': str(kwargs)[:100]
                    }
                )
                if reraise:
                    raise
                return return_on_error
        return wrapper
    return decorator


def safe_dataframe_operation(
    operation_name: str,
    default_df: Optional[pd.DataFrame] = None
) -> Callable:
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
            except Exception as e:
                logger.error(
                    f"Error in {operation_name}: {str(e)}",
                    extra={
                        'operation': operation_name,
                        'function': func.__name__,
                        'error_type': type(e).__name__
                    }
                )
                return default_df if default_df is not None else pd.DataFrame()
        return wrapper
    return decorator


def log_error_with_context(
    logger_instance: logging.Logger,
    message: str,
    error: Exception,
    context: Optional[dict] = None,
    level: int = logging.ERROR
) -> None:
    """
    Log an error with additional context information.
    
    Args:
        logger_instance: Logger to use
        message: Base error message
        error: The exception that occurred
        context: Additional context information
        level: Logging level
    """
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'original_message': message
    }
    
    if context:
        error_info.update(context)
    
    logger_instance.log(level, f"{message}: {str(error)}", extra=error_info)


def validate_dataframe_not_empty(df: pd.DataFrame, name: str) -> None:
    """
    Validate that a DataFrame is not empty.
    
    Args:
        df: DataFrame to validate
        name: Name of the DataFrame for error messages
        
    Raises:
        DataValidationError: If DataFrame is empty
    """
    if len(df) == 0:
        raise DataValidationError(
            column=name,
            message="DataFrame is empty",
            data_info=f"Shape: {df.shape}, Columns: {list(df.columns)}"
        )


def validate_required_columns(df: pd.DataFrame, required_columns: list, name: str) -> None:
    """
    Validate that a DataFrame contains required columns.
    
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
            data_info=f"Available columns: {list(df.columns)}"
        )


def safe_numeric_conversion(series: pd.Series, column_name: str) -> pd.Series:
    """
    Safely convert a pandas Series to numeric, with error handling.
    
    Args:
        series: Series to convert
        column_name: Name of the column for error messages
        
    Returns:
        Converted series with numeric values
        
    Raises:
        DataValidationError: If conversion fails completely
    """
    try:
        converted = pd.to_numeric(series, errors='coerce')
        
        # Check if all values became NaN
        if converted.isna().all() and not series.isna().all():
            raise DataValidationError(
                column=column_name,
                message="All values failed numeric conversion",
                data_info=f"Sample values: {series.head().tolist()}"
            )
        
        # Log warning if some values failed conversion
        failed_count = converted.isna().sum() - series.isna().sum()
        if failed_count > 0:
            logger.warning(
                f"Failed to convert {failed_count} values to numeric in column {column_name}",
                extra={'column': column_name, 'failed_count': failed_count}
            )
        
        return converted
    except Exception as e:
        raise DataValidationError(
            column=column_name,
            message=f"Numeric conversion failed: {str(e)}",
            data_info=f"Series dtype: {series.dtype}, length: {len(series)}"
        ) 