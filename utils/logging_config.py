"""Structured logging configuration with OpenTelemetry integration.

This module re-exports functionality from smaller helper modules to keep files
under 200 lines while preserving the original public API."""

from __future__ import annotations

from .logging_core import (
    setup_structured_logging,
    configure_logging,
    configure_for_development,
    configure_for_production,
    configure_for_testing,
    auto_configure,
)
from .logging_helpers import (
    _add_correlation_id,
    _add_performance_metrics,
    get_logger,
    LoggerMixin,
    log_performance,
)
from .logging_tracing import (
    _add_trace_context,
    _configure_tracing,
    _get_sampler,
    _get_otlp_headers,
    _log_hook,
    OPENTELEMETRY_AVAILABLE,
)
from .logging_operations import (
    LoggedOperation,
    log_operation_start,
    log_operation_success,
    log_operation_error,
    log_data_quality_issue,
    log_performance_metric,
)

__all__ = [
    "setup_structured_logging",
    "configure_logging",
    "configure_for_development",
    "configure_for_production",
    "configure_for_testing",
    "auto_configure",
    "get_logger",
    "LoggerMixin",
    "log_performance",
    "LoggedOperation",
    "log_operation_start",
    "log_operation_success",
    "log_operation_error",
    "log_data_quality_issue",
    "log_performance_metric",
]


if __name__ == "__main__":
    import time

    configure_for_development()

    main_logger = get_logger(__name__, component="logging_config", version="2025.1")

    main_logger.info("Structured logging configured", feature="enhanced_2025")
    main_logger.debug("Debug message", user_id=123, action="test")
    main_logger.warning("Warning message", error_code="W001")

    @log_performance
    def test_function() -> str:
        """Test function for performance logging."""
        time.sleep(0.1)
        return "success"

    test_function()

    def _test_exception() -> None:
        """Test exception for logging demonstration."""
        msg = "Test exception with enhanced context"
        raise ValueError(msg)

    try:
        _test_exception()
    except ValueError:
        main_logger.exception("Exception occurred", operation="test_exception", severity="high")
