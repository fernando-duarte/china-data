"""Structured logging configuration with OpenTelemetry integration.

This module re-exports functionality from smaller helper modules to keep files
under 200 lines while preserving the original public API.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from .logging_core import (
    auto_configure,
    configure_for_development,
    configure_for_production,
    configure_for_testing,
    configure_logging,
    setup_structured_logging,
)
from .logging_helpers import (
    LoggerMixin,
    get_logger,
    log_performance,
)
from .logging_operations import (
    LoggedOperation,
    log_data_quality_issue,
    log_operation_error,
    log_operation_start,
    log_operation_success,
    log_performance_metric,
)

F = TypeVar("F", bound=Callable[..., Any])

__all__ = [
    "LoggedOperation",
    "LoggerMixin",
    "auto_configure",
    "configure_for_development",
    "configure_for_production",
    "configure_for_testing",
    "configure_logging",
    "get_logger",
    "log_data_quality_issue",
    "log_operation_error",
    "log_operation_start",
    "log_operation_success",
    "log_performance",
    "log_performance_metric",
    "setup_structured_logging",
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
