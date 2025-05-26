"""Structured logging configuration with OpenTelemetry integration.

This module provides production-ready structured logging configuration
for the China data analysis pipeline.
"""

import logging
import os
import sys
from typing import Any

import structlog
from opentelemetry import trace  # pylint: disable=import-error
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # pylint: disable=import-error
from opentelemetry.instrumentation.logging import LoggingInstrumentor  # pylint: disable=import-error
from opentelemetry.sdk.resources import Resource  # pylint: disable=import-error
from opentelemetry.sdk.trace import TracerProvider  # pylint: disable=import-error
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # pylint: disable=import-error


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
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add tracing context if enabled
    if enable_tracing:
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
    if enable_tracing:
        service_name = kwargs.get("service_name", "china-data-pipeline")
        service_version = kwargs.get("service_version", "1.0.0")
        otlp_endpoint = kwargs.get("otlp_endpoint")
        _configure_tracing(service_name, service_version, otlp_endpoint)


def _add_trace_context(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add OpenTelemetry trace context to log records."""
    span = trace.get_current_span()
    if span != trace.INVALID_SPAN:
        span_context = span.get_span_context()
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
    return event_dict


def _configure_tracing(service_name: str, service_version: str, otlp_endpoint: str | None) -> None:
    """Configure OpenTelemetry tracing."""
    # Create resource with service information
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "service.instance.id": os.getenv("HOSTNAME", "unknown"),
        }
    )

    # Configure tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Configure span exporter
    if otlp_endpoint:
        # Use OTLP exporter for production
        span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    else:
        # Use console exporter for development
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        span_exporter = ConsoleSpanExporter()

    # Add span processor
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Instrument logging
    LoggingInstrumentor().instrument(set_logging_format=True)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structured logger
    """
    return structlog.get_logger(name)


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


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    configure_for_development()

    # Get logger
    logger = get_logger(__name__)

    # Test logging
    logger.info("Structured logging configured", component="logging_config")
    logger.debug("Debug message", user_id=123, action="test")
    logger.warning("Warning message", error_code="W001")

    def _test_exception() -> None:
        """Test exception for logging demonstration."""
        msg = "Test exception"
        raise ValueError(msg)

    try:
        _test_exception()
    except ValueError:
        logger.exception("Exception occurred", operation="test_exception")
