"""Helper utilities for structured logging."""

from __future__ import annotations

import contextlib
import functools
import os
import time
from collections.abc import Callable
from typing import Any

import structlog


def _add_correlation_id(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add correlation ID for request tracing."""
    correlation_id = (
        os.getenv("CORRELATION_ID")
        or getattr(_logger, "_correlation_id", None)
        or event_dict.get("correlation_id")
    )

    if correlation_id:
        event_dict["correlation_id"] = correlation_id

    return event_dict


def _add_performance_metrics(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add performance metrics context."""
    with contextlib.suppress(ImportError, OSError):
        import psutil

        event_dict["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "timestamp": time.time(),
        }

    return event_dict


def get_logger(name: str | None = None, **context: Any) -> Any:
    """Get a structured logger instance with optional context."""
    if name is None:
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "unknown")

    bound_logger = structlog.get_logger(name or "unknown")
    if context:
        bound_logger = bound_logger.bind(**context)
    return bound_logger


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
        except Exception as e:  # noqa: BLE001
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
        perf_logger.info(
            "Function completed",
            function=func.__name__,
            duration_seconds=duration,
            status="success",
        )
        return result

    return wrapper
