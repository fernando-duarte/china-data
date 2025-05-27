"""Utilities for logging operations and metrics."""

from __future__ import annotations

import time
import types
from typing import Any


class LoggedOperation:
    """Context manager for logging operation start, success, and failure."""

    def __init__(self, logger: Any, operation_name: str, **context: Any) -> None:
        """Initialize the logged operation."""
        self.logger = logger
        self.operation_name = operation_name
        self.context = context
        self.start_time = 0.0

    def __enter__(self) -> Any:
        """Enter the context and log operation start."""
        self.start_time = time.time()
        self.logger.info("Operation started", operation=self.operation_name, **self.context)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit the context and log operation completion or failure."""
        duration = time.time() - self.start_time

        if exc_type is None:
            self.logger.info(
                "Operation completed successfully",
                operation=self.operation_name,
                duration_seconds=duration,
                **self.context,
            )
        else:
            self.logger.error(
                "Operation failed",
                operation=self.operation_name,
                duration_seconds=duration,
                error_type=exc_type.__name__ if exc_type else "Unknown",
                error_message=str(exc_val) if exc_val else "Unknown error",
                **self.context,
            )


def log_operation_start(logger: Any, operation_name: str, **context: Any) -> Any:
    """Log the start of an operation."""
    bound_logger = logger.bind(operation=operation_name, **context)
    bound_logger.info("Operation started")
    return bound_logger


def log_operation_success(
    logger: Any,
    operation_name: str,
    duration_seconds: float | None = None,
    **context: Any,
) -> None:
    """Log successful completion of an operation."""
    log_data = {"operation": operation_name, **context}
    if duration_seconds is not None:
        log_data["duration_seconds"] = duration_seconds

    logger.info("Operation completed successfully", **log_data)


def log_operation_error(
    logger: Any,
    operation_name: str,
    error: Exception,
    duration_seconds: float | None = None,
    **context: Any,
) -> None:
    """Log an operation error."""
    log_data = {
        "operation": operation_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        **context,
    }
    if duration_seconds is not None:
        log_data["duration_seconds"] = duration_seconds

    logger.error("Operation failed", **log_data)


def log_data_quality_issue(
    logger: Any,
    issue_type: str,
    description: str,
    *,
    data_source: str | None = None,
    affected_records: int | None = None,
    column: str | None = None,
    **context: Any,
) -> None:
    """Log a data quality issue."""
    log_data = {
        "issue_type": issue_type,
        "description": description,
        **context,
    }

    if data_source:
        log_data["data_source"] = data_source
    if affected_records is not None:
        log_data["affected_records"] = affected_records
    if column:
        log_data["column"] = column

    logger.warning("Data quality issue detected", **log_data)


def log_performance_metric(
    logger: Any,
    metric_name: str,
    value: float,
    unit: str,
    operation: str | None = None,
    **context: Any,
) -> None:
    """Log a performance metric."""
    log_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        **context,
    }

    if operation:
        log_data["operation"] = operation

    logger.info("Performance metric", **log_data)
