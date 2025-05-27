"""Structured logging configuration with OpenTelemetry integration.

This module provides production-ready structured logging configuration
for the China data analysis pipeline following 2025 best practices.
"""

import contextlib
import functools
import logging
import os
import sys
import time
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any

import structlog

try:
    from opentelemetry import trace  # pylint: disable=import-error
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,  # pylint: disable=import-error,no-name-in-module
    )
    from opentelemetry.instrumentation.logging import (
        LoggingInstrumentor,  # pylint: disable=import-error,no-name-in-module
    )
    from opentelemetry.sdk.resources import Resource  # pylint: disable=import-error
    from opentelemetry.sdk.trace import TracerProvider  # pylint: disable=import-error
    from opentelemetry.sdk.trace.export import BatchSpanProcessor  # pylint: disable=import-error

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False


def setup_structured_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    enable_json: bool = False,
    enable_console: bool = True,
    include_process_info: bool = False,
) -> None:
    """Set up structured logging with the expected signature for backward compatibility.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_json: Whether to use JSON format
        enable_console: Whether to enable console output
        include_process_info: Whether to include process information
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout if enable_console else None,
        level=getattr(logging, log_level.upper()),
    )

    # Configure processors
    processors: list[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _add_correlation_id,
    ]

    # Add process info if requested
    if include_process_info:
        processors.append(_add_performance_metrics)

    # Add final renderer based on format type
    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure file logging if specified
    if log_file:
        file_handler = logging.FileHandler(Path(log_file))
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)


def configure_logging(
    level: str = "INFO",
    format_type: str = "json",
    enable_tracing: bool = False,
    **kwargs: Any,
) -> None:
    """Configure structured logging with optional OpenTelemetry integration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format ('json' for production, 'console' for development)
        enable_tracing: Whether to enable OpenTelemetry tracing
        **kwargs: Additional configuration options (service_name, service_version, otlp_endpoint)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Configure processors based on format type
    processors: list[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _add_correlation_id,  # Add correlation ID for request tracing
        _add_performance_metrics,  # Add performance context
    ]

    # Add tracing context if enabled
    if enable_tracing and OPENTELEMETRY_AVAILABLE:
        processors.append(_add_trace_context)

    # Add final renderer based on format type
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure OpenTelemetry if enabled
    if enable_tracing and OPENTELEMETRY_AVAILABLE:
        service_name = kwargs.get("service_name", "china-data-pipeline")
        service_version = kwargs.get("service_version", "1.0.0")
        otlp_endpoint = kwargs.get("otlp_endpoint")
        _configure_tracing(service_name, service_version, otlp_endpoint)


def _add_correlation_id(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add correlation ID for request tracing."""
    # Try to get correlation ID from various sources
    correlation_id = (
        os.getenv("CORRELATION_ID") or getattr(_logger, "_correlation_id", None) or event_dict.get("correlation_id")
    )

    if correlation_id:
        event_dict["correlation_id"] = correlation_id

    return event_dict


def _add_performance_metrics(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add performance metrics context."""
    # Add system metrics for performance monitoring
    with contextlib.suppress(ImportError, OSError):
        import psutil

        event_dict["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "timestamp": time.time(),
        }

    return event_dict


def _add_trace_context(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add OpenTelemetry trace context to log records."""
    if not OPENTELEMETRY_AVAILABLE:
        return event_dict

    span = trace.get_current_span()
    if span != trace.INVALID_SPAN:
        span_context = span.get_span_context()
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")

        # Add trace flags for sampling decisions
        event_dict["trace_flags"] = span_context.trace_flags
    return event_dict


def _configure_tracing(service_name: str, service_version: str, otlp_endpoint: str | None) -> None:
    """Configure OpenTelemetry tracing with enhanced 2025 practices."""
    if not OPENTELEMETRY_AVAILABLE:
        return

    # Create resource with comprehensive service information
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "service.instance.id": os.getenv("HOSTNAME", "unknown"),
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.language": "python",
            "telemetry.sdk.version": "1.0.0",
        }
    )

    # Configure tracer provider with sampling
    tracer_provider = TracerProvider(
        resource=resource,
        # Add sampling for production environments
        sampler=_get_sampler(),
    )
    trace.set_tracer_provider(tracer_provider)

    # Configure span exporter with retry and batching
    if otlp_endpoint:
        # Use OTLP exporter for production with enhanced configuration
        span_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            headers=_get_otlp_headers(),
            timeout=30,  # 30 second timeout
        )
    else:
        # Use console exporter for development
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        span_exporter = ConsoleSpanExporter()

    # Add span processor with optimized batching
    span_processor = BatchSpanProcessor(
        span_exporter,
        max_queue_size=2048,
        max_export_batch_size=512,
        export_timeout_millis=30000,
        schedule_delay_millis=5000,
    )
    tracer_provider.add_span_processor(span_processor)

    # Instrument logging with enhanced configuration
    LoggingInstrumentor().instrument(
        set_logging_format=True,
        log_hook=_log_hook,
    )


def _get_sampler() -> Any:
    """Get appropriate sampler based on environment."""
    if not OPENTELEMETRY_AVAILABLE:
        return None

    from opentelemetry.sdk.trace.sampling import ALWAYS_OFF, ALWAYS_ON, TraceIdRatioBased

    env = os.getenv("ENVIRONMENT", "development").lower()
    sample_rate = float(os.getenv("TRACE_SAMPLE_RATE", "1.0"))

    if env == "production":
        # Use rate-based sampling in production
        return TraceIdRatioBased(sample_rate)
    if env == "testing":
        # Disable tracing in tests unless explicitly enabled
        return ALWAYS_OFF if not os.getenv("ENABLE_TRACING_IN_TESTS") else ALWAYS_ON
    # Always trace in development
    return ALWAYS_ON


def _get_otlp_headers() -> dict[str, str]:
    """Get OTLP headers for authentication and metadata."""
    headers = {}

    # Add authentication if API key is provided
    api_key = os.getenv("OTLP_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Add custom headers
    custom_headers = os.getenv("OTLP_HEADERS")
    if custom_headers:
        for header in custom_headers.split(","):
            if "=" in header:
                key, value = header.split("=", 1)
                headers[key.strip()] = value.strip()

    return headers


def _log_hook(span: Any, record: Any) -> None:
    """Hook to add span information to log records."""
    if span and span.is_recording():
        # Add span attributes to log record
        record.span_id = format(span.get_span_context().span_id, "016x")
        record.trace_id = format(span.get_span_context().trace_id, "032x")


def get_logger(name: str | None = None, **context: Any) -> Any:
    """Get a structured logger instance with optional context.

    Args:
        name: Logger name (typically __name__). If None, will auto-detect from caller.
        **context: Additional context to bind to the logger

    Returns:
        Configured structured logger with bound context
    """
    if name is None:
        # Auto-detect caller name
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "unknown")

    bound_logger = structlog.get_logger(name or "unknown")
    if context:
        bound_logger = bound_logger.bind(**context)
    return bound_logger


def configure_for_development() -> None:
    """Configure logging for development environment."""
    configure_logging(
        level="DEBUG",
        format_type="console",
        enable_tracing=False,
    )


def configure_for_production() -> None:
    """Configure logging for production environment."""
    configure_logging(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format_type="json",
        enable_tracing=True,
        service_name=os.getenv("SERVICE_NAME", "china-data-pipeline"),
        service_version=os.getenv("SERVICE_VERSION", "1.0.0"),
        otlp_endpoint=os.getenv("OTLP_ENDPOINT"),
    )


def configure_for_testing() -> None:
    """Configure logging for testing environment."""
    configure_logging(
        level="WARNING",  # Reduce noise in tests
        format_type="console",
        enable_tracing=False,
    )


# Auto-configure based on environment
def auto_configure() -> None:
    """Automatically configure logging based on environment variables."""
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        configure_for_production()
    elif env == "testing":
        configure_for_testing()
    else:
        configure_for_development()


class LoggerMixin:
    """Mixin class to add structured logging to any class."""

    @property
    def logger(self) -> Any:
        """Get a logger bound to this class."""
        if not hasattr(self, "_logger"):
            class_name = self.__class__.__name__
            module_name = self.__class__.__module__
            self._logger = get_logger(f"{module_name}.{class_name}")
        return self._logger


def log_performance(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[misc]
    """Decorator to log function performance metrics."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        perf_logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            duration = time.time() - start_time
            perf_logger.exception(
                "Function failed",
                function=func.__name__,
                duration_seconds=duration,
                status="error",
                error=str(e),
            )
            raise

        duration = time.time() - start_time
        perf_logger.info("Function completed", function=func.__name__, duration_seconds=duration, status="success")
        return result

    return wrapper


class LoggedOperation:
    """Context manager for logging operation start, success, and failure."""

    def __init__(self, logger: Any, operation_name: str, **context: Any) -> None:
        """Initialize the logged operation.

        Args:
            logger: The logger instance to use
            operation_name: Name of the operation being logged
            **context: Additional context to include in logs
        """
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
    """Log the start of an operation.

    Args:
        logger: The logger instance
        operation_name: Name of the operation
        **context: Additional context

    Returns:
        Logger bound with operation context
    """
    bound_logger = logger.bind(operation=operation_name, **context)
    bound_logger.info("Operation started")
    return bound_logger


def log_operation_success(
    logger: Any,
    operation_name: str,
    duration_seconds: float | None = None,
    **context: Any,
) -> None:
    """Log successful completion of an operation.

    Args:
        logger: The logger instance
        operation_name: Name of the operation
        duration_seconds: Optional duration in seconds
        **context: Additional context
    """
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
    """Log an operation error.

    Args:
        logger: The logger instance
        operation_name: Name of the operation
        error: The exception that occurred
        duration_seconds: Optional duration in seconds
        **context: Additional context
    """
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
    """Log a data quality issue.

    Args:
        logger: The logger instance
        issue_type: Type of data quality issue
        description: Description of the issue
        data_source: Optional data source name
        affected_records: Optional number of affected records
        column: Optional column name
        **context: Additional context
    """
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
    """Log a performance metric.

    Args:
        logger: The logger instance
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        operation: Optional operation name
        **context: Additional context
    """
    log_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        **context,
    }

    if operation:
        log_data["operation"] = operation

    logger.info("Performance metric", **log_data)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    configure_for_development()

    # Get logger with context
    main_logger = get_logger(__name__, component="logging_config", version="2025.1")

    # Test logging with enhanced features
    main_logger.info("Structured logging configured", feature="enhanced_2025")
    main_logger.debug("Debug message", user_id=123, action="test")
    main_logger.warning("Warning message", error_code="W001")

    # Test performance logging
    @log_performance
    def test_function() -> str:
        """Test function for performance logging."""
        time.sleep(0.1)
        return "success"

    test_function()

    # Test exception logging
    def _test_exception() -> None:
        """Test exception for logging demonstration."""
        msg = "Test exception with enhanced context"
        raise ValueError(msg)

    try:
        _test_exception()
    except ValueError:
        main_logger.exception("Exception occurred", operation="test_exception", severity="high")
