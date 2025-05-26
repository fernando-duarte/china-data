"""
Custom exception classes for China data processing.

This module defines all custom exceptions used throughout the China data
processing pipeline for consistent error handling.
"""

from typing import Optional


class ChinaDataError(Exception):
    """Base exception for China data processing errors."""


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
