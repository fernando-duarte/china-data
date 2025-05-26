"""Structured logging configuration for China Data Processing.

This module provides structured logging setup using structlog for better
observability, debugging, and monitoring of the data processing pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Optional

import structlog
from structlog.types import EventDict, Processor

from config import Config


def add_timestamp(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add timestamp to log events."""
    import time

    event_dict["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return event_dict


def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to event dict."""
    event_dict["level"] = method_name.upper()
    return event_dict


def add_module_info(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add module and function information to log events."""
    import inspect

    # Get the calling frame (skip structlog internal frames)
    frame = inspect.currentframe()
    try:
        # Skip through structlog frames to find the actual caller
        while frame and (
            frame.f_code.co_filename.endswith("structlog")
            or "structlog" in frame.f_code.co_filename
            or frame.f_code.co_name in ["_process_event", "_proxy_method", "add_module_info"]
        ):
            frame = frame.f_back

        if frame:
            event_dict["module"] = Path(frame.f_code.co_filename).stem
            event_dict["function"] = frame.f_code.co_name
            event_dict["line"] = frame.f_lineno
    finally:
        del frame

    return event_dict


def add_process_info(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add process information to log events."""
    import os

    event_dict["pid"] = os.getpid()
    return event_dict


def filter_by_level(min_level: int = logging.INFO) -> Processor:
    """Create a processor that filters events by minimum log level."""

    def processor(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }

        current_level = level_map.get(method_name.lower(), logging.INFO)
        if current_level < min_level:
            raise structlog.DropEvent

        return event_dict

    return processor


def setup_structured_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    enable_console: bool = True,
    enable_json: bool = False,
    include_process_info: bool = True,
) -> None:
    """Configure structured logging for the application.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        enable_console: Whether to enable console output
        enable_json: Whether to use JSON format (useful for log aggregation)
        include_process_info: Whether to include process information in logs
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        level=numeric_level,
        format="%(message)s",  # structlog will handle formatting
        handlers=[],  # We'll add handlers below
    )

    # Build processor chain
    processors = [
        add_timestamp,
        add_log_level,
        add_module_info,
        filter_by_level(numeric_level),
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
    ]

    if include_process_info:
        processors.append(add_process_info)

    # Add final processor based on output format
    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=enable_console and sys.stderr.isatty(),
                exception_formatter=structlog.dev.plain_traceback,
            )
        )

    # Set up handlers for standard library logging
    handlers = []

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        handlers.append(console_handler)

    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding=Config.FILE_ENCODING)
        file_handler.setLevel(numeric_level)
        handlers.append(file_handler)

    # Configure root logger with our handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    for handler in handlers:
        root_logger.addHandler(handler)

    # Configure structlog to use the standard library logging
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (defaults to calling module name)

    Returns:
        Configured structlog BoundLogger instance
    """
    if name is None:
        import inspect

        frame = inspect.currentframe()
        try:
            if frame and frame.f_back:
                name = Path(frame.f_back.f_code.co_filename).stem
        finally:
            del frame

    return structlog.get_logger(name)


def log_operation_start(logger: structlog.BoundLogger, operation: str, **context: Any) -> structlog.BoundLogger:
    """Log the start of an operation with context.

    Args:
        logger: Structured logger instance
        operation: Name of the operation
        **context: Additional context to include

    Returns:
        Logger bound with operation context
    """
    bound_logger = logger.bind(operation=operation, **context)
    bound_logger.info("Operation started", operation=operation)
    return bound_logger


def log_operation_success(
    logger: structlog.BoundLogger, operation: str, duration_seconds: float | None = None, **context: Any
) -> None:
    """Log successful completion of an operation.

    Args:
        logger: Structured logger instance
        operation: Name of the operation
        duration_seconds: Optional operation duration
        **context: Additional context to include
    """
    log_data = {"operation": operation, **context}
    if duration_seconds is not None:
        log_data["duration_seconds"] = round(duration_seconds, 3)

    logger.info("Operation completed successfully", **log_data)


def log_operation_error(
    logger: structlog.BoundLogger,
    operation: str,
    error: Exception,
    duration_seconds: float | None = None,
    **context: Any,
) -> None:
    """Log operation failure with error details.

    Args:
        logger: Structured logger instance
        operation: Name of the operation
        error: The exception that occurred
        duration_seconds: Optional operation duration
        **context: Additional context to include
    """
    log_data = {"operation": operation, "error_type": type(error).__name__, "error_message": str(error), **context}
    if duration_seconds is not None:
        log_data["duration_seconds"] = round(duration_seconds, 3)

    logger.error("Operation failed", **log_data, exc_info=True)


def log_data_quality_issue(
    logger: structlog.BoundLogger,
    issue_type: str,
    description: str,
    data_source: str | None = None,
    affected_records: int | None = None,
    **context: Any,
) -> None:
    """Log data quality issues with structured context.

    Args:
        logger: Structured logger instance
        issue_type: Type of data quality issue (e.g., 'missing_data', 'outlier', 'validation_error')
        description: Human-readable description of the issue
        data_source: Optional data source identifier
        affected_records: Optional number of affected records
        **context: Additional context to include
    """
    log_data = {"issue_type": issue_type, "description": description, **context}

    if data_source:
        log_data["data_source"] = data_source
    if affected_records is not None:
        log_data["affected_records"] = affected_records

    logger.warning("Data quality issue detected", **log_data)


def log_performance_metric(
    logger: structlog.BoundLogger, metric_name: str, metric_value: float, metric_unit: str = "seconds", **context: Any
) -> None:
    """Log performance metrics with structured context.

    Args:
        logger: Structured logger instance
        metric_name: Name of the performance metric
        metric_value: Numeric value of the metric
        metric_unit: Unit of measurement
        **context: Additional context to include
    """
    logger.info(
        "Performance metric",
        metric_name=metric_name,
        metric_value=round(metric_value, 3),
        metric_unit=metric_unit,
        **context,
    )


# Context managers for operation logging
class LoggedOperation:
    """Context manager for logging operations with automatic timing."""

    def __init__(self, logger: structlog.BoundLogger, operation: str, **context: Any):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time: float | None = None
        self.bound_logger: structlog.BoundLogger | None = None

    def __enter__(self) -> structlog.BoundLogger:
        import time

        self.start_time = time.time()
        self.bound_logger = log_operation_start(self.logger, self.operation, **self.context)
        return self.bound_logger

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        import time

        duration = time.time() - (self.start_time or 0)

        if exc_type is None:
            log_operation_success(
                self.bound_logger or self.logger, self.operation, duration_seconds=duration, **self.context
            )
        else:
            log_operation_error(
                self.bound_logger or self.logger, self.operation, exc_val, duration_seconds=duration, **self.context
            )
