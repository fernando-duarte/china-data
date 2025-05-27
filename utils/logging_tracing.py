"""OpenTelemetry tracing helpers for structured logging."""

from __future__ import annotations

import os
from typing import Any

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
except ImportError:  # pragma: no cover - optional dependency
    OPENTELEMETRY_AVAILABLE = False


def _add_trace_context(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add OpenTelemetry trace context to log records."""
    if not OPENTELEMETRY_AVAILABLE:
        return event_dict

    span = trace.get_current_span()
    if span != trace.INVALID_SPAN:
        span_context = span.get_span_context()
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
        event_dict["trace_flags"] = span_context.trace_flags
    return event_dict


def _configure_tracing(service_name: str, service_version: str, otlp_endpoint: str | None) -> None:
    """Configure OpenTelemetry tracing with enhanced 2025 practices."""
    if not OPENTELEMETRY_AVAILABLE:
        return

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

    tracer_provider = TracerProvider(
        resource=resource,
        sampler=_get_sampler(),
    )
    trace.set_tracer_provider(tracer_provider)

    if otlp_endpoint:
        span_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            headers=_get_otlp_headers(),
            timeout=30,
        )
    else:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        span_exporter = ConsoleSpanExporter()

    span_processor = BatchSpanProcessor(
        span_exporter,
        max_queue_size=2048,
        max_export_batch_size=512,
        export_timeout_millis=30000,
        schedule_delay_millis=5000,
    )
    tracer_provider.add_span_processor(span_processor)

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
        return TraceIdRatioBased(sample_rate)
    if env == "testing":
        return ALWAYS_OFF if not os.getenv("ENABLE_TRACING_IN_TESTS") else ALWAYS_ON
    return ALWAYS_ON


def _get_otlp_headers() -> dict[str, str]:
    """Get OTLP headers for authentication and metadata."""
    headers: dict[str, str] = {}

    api_key = os.getenv("OTLP_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

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
        record.span_id = format(span.get_span_context().span_id, "016x")
        record.trace_id = format(span.get_span_context().trace_id, "032x")

