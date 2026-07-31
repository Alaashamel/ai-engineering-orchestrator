from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_tracer: trace.Tracer | None = None


def setup_tracing(
    service_name: str = "ai-software-engineering",
    endpoint: str | None = None,
) -> trace.Tracer:
    global _tracer
    if _tracer is not None:
        return _tracer

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if endpoint:
        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name)
    return _tracer


def get_tracer() -> trace.Tracer:
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("ai-software-engineering")
    return _tracer


@asynccontextmanager
async def trace_phase(
    phase_name: str,
    project_id: str,
    attributes: dict[str, Any] | None = None,
) -> AsyncIterator[trace.Span]:
    tracer = get_tracer()
    attrs = {"project_id": project_id, "phase": phase_name}
    if attributes:
        attrs.update(attributes)
    with tracer.start_as_current_span(f"phase.{phase_name}", attributes=attrs) as span:
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise


@asynccontextmanager
async def trace_agent(
    agent_name: str,
    project_id: str,
    attributes: dict[str, Any] | None = None,
) -> AsyncIterator[trace.Span]:
    tracer = get_tracer()
    attrs = {"project_id": project_id, "agent": agent_name}
    if attributes:
        attrs.update(attributes)
    with tracer.start_as_current_span(f"agent.{agent_name}", attributes=attrs) as span:
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
