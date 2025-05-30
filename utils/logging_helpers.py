"""Helper utilities for structured logging."""

from __future__ import annotations

import contextlib
import functools
import inspect
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar, cast

import structlog

# Optional import for psutil
try:
    import psutil
except ImportError:
    psutil = None

F = TypeVar("F", bound=Callable[..., Any])


def _add_correlation_id(
    _logger: Any, _method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add correlation ID for request tracing."""
    correlation_id = (
        os.getenv("CORRELATION_ID")
        or getattr(_logger, "_correlation_id", None)
        or event_dict.get("correlation_id")
    )

    if correlation_id:
        event_dict["correlation_id"] = correlation_id

    return event_dict


def _add_performance_metrics(
    _logger: Any, _method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add performance metrics context."""
    if psutil:
        with contextlib.suppress(OSError):  # Only suppress OSError now
            event_dict["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory_percent": psutil.virtual_memory().percent,
                "timestamp": time.time(),
            }
    return event_dict


def get_logger(name: str | None = None, **context: Any) -> Any:
    """Get a structured logger instance with optional context."""
    if name is None:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "unknown")

    bound_logger = structlog.get_logger(name or "unknown")
    if context:
        bound_logger = bound_logger.bind(**context)
    return bound_logger


class LoggerMixin:  # pylint: disable=too-few-public-methods
    """Provides a logger for subclasses."""

    @property
    def logger(self) -> Any:
        """Get a logger bound to this class."""
        if not hasattr(self, "_logger"):
            class_name = self.__class__.__name__
            module_name = self.__class__.__module__
            self._logger = get_logger(f"{module_name}.{class_name}")
        return self._logger


def log_performance(func: F) -> F:
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
        perf_logger.info(
            "Function completed",
            function=func.__name__,
            duration_seconds=duration,
            status="success",
        )
        return result

    return cast("F", wrapper)


def _add_module_info(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add module, function, and line information to log events."""
    # Get the stack, skipping logging-related frames
    frame = None
    for frame_info in inspect.stack()[1:]:  # Skip the current frame
        filename = frame_info.filename
        function_name = frame_info.function

        # Skip logging infrastructure, structlog frames, and test infrastructure
        # Look for the first user code frame
        skip_patterns = [
            "structlog",
            "logging",
            "logging_",
            "pytest",
            "_pytest",
            "pluggy",
            "python3",
            "python.app",
            "__pypackages__",
            "site-packages",
        ]
        skip_functions = ["pytest_pyfunc_call", "_call_impl", "_hookexec"]

        if (
            not any(pattern in filename for pattern in skip_patterns)
            and function_name not in skip_functions
        ):
            frame = frame_info
            break

    if frame:
        # Extract module name from filename
        basename = Path(frame.filename).name
        module_name = basename.replace(".py", "")

        event_dict["module"] = module_name
        event_dict["function"] = frame.function
        event_dict["line"] = frame.lineno

    return event_dict
