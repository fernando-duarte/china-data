"""Core structured logging configuration functions."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

import structlog

from .logging_helpers import _add_correlation_id, _add_performance_metrics
from .logging_tracing import (
    OPENTELEMETRY_AVAILABLE,
    _add_trace_context,
    _configure_tracing,
)


def setup_structured_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    enable_json: bool = False,
    enable_console: bool = True,
    include_process_info: bool = False,
) -> None:
    """Set up structured logging with the expected signature for backward compatibility."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout if enable_console else None,
        level=getattr(logging, log_level.upper()),
    )

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

    if include_process_info:
        processors.append(_add_performance_metrics)

    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

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
    """Configure structured logging with optional OpenTelemetry integration."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

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
        _add_performance_metrics,
    ]

    if enable_tracing and OPENTELEMETRY_AVAILABLE:
        processors.append(_add_trace_context)

    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    if enable_tracing and OPENTELEMETRY_AVAILABLE:
        service_name = kwargs.get("service_name", "china-data-pipeline")
        service_version = kwargs.get("service_version", "1.0.0")
        otlp_endpoint = kwargs.get("otlp_endpoint")
        _configure_tracing(service_name, service_version, otlp_endpoint)


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
        level="WARNING",
        format_type="console",
        enable_tracing=False,
    )


def auto_configure() -> None:
    """Automatically configure logging based on environment variables."""
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        configure_for_production()
    elif env == "testing":
        configure_for_testing()
    else:
        configure_for_development()
