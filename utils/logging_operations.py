"""Utilities for logging operations and metrics."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import types

# Remove the cyclic import - this module should not import from logging_config
# since logging_config imports from this module
module_logger = logging.getLogger(__name__)


class LoggedOperation:
    """Context manager for logging operation start, success, and failure."""

    def __init__(self, operation_logger: Any, operation_name: str, **context: Any) -> None:
        """Initialize the logged operation."""
        self.logger = operation_logger
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


def log_operation_start(operation_logger: Any, operation_name: str, **context: Any) -> Any:
    """Log the start of an operation."""
    bound_logger = operation_logger.bind(operation=operation_name, **context)
    bound_logger.info("Operation started")
    return bound_logger


def log_operation_success(
    operation_logger: Any,
    operation_name: str,
    duration_seconds: float | None = None,
    **context: Any,
) -> None:
    """Log successful completion of an operation."""
    log_data = {"operation": operation_name, **context}
    if duration_seconds is not None:
        log_data["duration_seconds"] = duration_seconds

    operation_logger.info("Operation completed successfully", **log_data)


def log_operation_error(
    operation_logger: Any,
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

    operation_logger.error("Operation failed", **log_data)


def log_data_quality_issue(
    operation_logger: Any,
    issue_type: str,
    description: str,
    details: dict[str, Any] | None = None,
    **context: Any,
) -> None:
    """Log a data quality issue."""
    log_data = {
        "issue_type": issue_type,
        "description": description,
        **context,
    }

    if details:
        log_data.update(details)

    operation_logger.warning("Data quality issue detected", **log_data)


def log_performance_metric(
    operation_logger: Any,
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

    operation_logger.info("Performance metric", **log_data)
