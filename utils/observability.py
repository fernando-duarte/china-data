"""OpenTelemetry observability configuration for China Data Pipeline.

This module provides structured logging, metrics, and tracing capabilities
using OpenTelemetry for comprehensive observability.
"""

# mypy: disable-error-code=no-any-unimported

import os
import sys
import types
from collections.abc import Callable
from typing import Any, TypeVar

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

F = TypeVar("F", bound=Callable[..., Any])


def configure_observability() -> None:
    """Configure OpenTelemetry tracing and metrics for the application."""
    # Resource attributes for service identification
    resource = Resource.create(
        {
            "service.name": "china-data-pipeline",
            "service.version": os.getenv("CHINA_DATA_VERSION", "0.1.0"),
            "service.environment": os.getenv("ENVIRONMENT", "development"),
            "service.instance.id": os.getenv("INSTANCE_ID", "local"),
        }
    )

    # Configure tracing
    _configure_tracing(resource)

    # Configure metrics
    _configure_metrics(resource)


def _configure_tracing(resource: Resource) -> None:
    """Configure OpenTelemetry tracing."""
    # Set up trace provider
    trace_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(trace_provider)

    # Configure OTLP exporter if endpoint is provided
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            headers=_get_otlp_headers(),
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace_provider.add_span_processor(span_processor)


def _configure_metrics(resource: Resource) -> None:
    """Configure OpenTelemetry metrics."""
    # Configure OTLP metric exporter if endpoint is provided
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        metric_exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            headers=_get_otlp_headers(),
        )
        metric_reader = PeriodicExportingMetricReader(
            exporter=metric_exporter,
            export_interval_millis=30000,  # Export every 30 seconds
        )
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
        )
    else:
        # Use default meter provider for development
        meter_provider = MeterProvider(resource=resource)

    metrics.set_meter_provider(meter_provider)


def _get_otlp_headers() -> dict[str, str] | None:
    """Get OTLP headers from environment variables."""
    headers_env = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
    if headers_env:
        headers = {}
        for header_pair in headers_env.split(","):
            if "=" in header_pair:
                key, value = header_pair.split("=", 1)
                headers[key.strip()] = value.strip()
        return headers
    return None


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance for the given name."""
    return trace.get_tracer(name)


def get_meter(name: str) -> metrics.Meter:
    """Get a meter instance for the given name."""
    return metrics.get_meter(name)


# Application metrics
def create_application_metrics() -> dict[str, Any]:
    """Create standard application metrics."""
    meter = get_meter("china_data")

    return {
        # Counters
        "data_downloads_total": meter.create_counter(
            "data_downloads_total",
            description="Total number of data downloads attempted",
            unit="1",
        ),
        "data_processing_total": meter.create_counter(
            "data_processing_total",
            description="Total number of data processing operations",
            unit="1",
        ),
        "errors_total": meter.create_counter(
            "errors_total",
            description="Total number of errors encountered",
            unit="1",
        ),
        # Histograms
        "download_duration": meter.create_histogram(
            "download_duration_seconds",
            description="Duration of data download operations",
            unit="s",
        ),
        "processing_duration": meter.create_histogram(
            "processing_duration_seconds",
            description="Duration of data processing operations",
            unit="s",
        ),
        # Gauges (via UpDownCounter for simplicity)
        "active_downloads": meter.create_up_down_counter(
            "active_downloads",
            description="Number of active download operations",
            unit="1",
        ),
        "memory_usage": meter.create_gauge(
            "memory_usage_bytes",
            description="Current memory usage",
            unit="byte",
        ),
    }


# Context managers for tracing
class TracedOperation:
    """Context manager for tracing operations."""

    def __init__(self, operation_name: str, tracer_name: str = "china_data") -> None:
        self.operation_name = operation_name
        self.tracer = get_tracer(tracer_name)
        self.span: trace.Span | None = None

    def __enter__(self) -> trace.Span:
        self.span = self.tracer.start_span(self.operation_name)
        return self.span

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        if self.span:
            if exc_type:
                self.span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc_val)))
                if exc_val:
                    self.span.record_exception(exc_val)
            else:
                self.span.set_status(trace.Status(trace.StatusCode.OK))
            self.span.end()


def trace_function(
    operation_name: str | None = None, tracer_name: str = "china_data"
) -> Callable[[F], F]:
    """Decorator to trace function execution."""

    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            name = operation_name or f"{func.__module__}.{func.__name__}"
            with TracedOperation(name, tracer_name):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


# Initialize observability if not in test mode
if "pytest" not in sys.modules and os.getenv("OTEL_ENABLED", "true").lower() == "true":
    configure_observability()
