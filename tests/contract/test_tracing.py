"""Distributed tracing tests (FR-040, TM104–TM106)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from src.observability.tracing import (
    TracingConfig,
    configure_tracing,
    instrument_app,
)

pytestmark = [pytest.mark.unit, pytest.mark.trace]

REPO_ROOT = Path(__file__).resolve().parents[2]


def _traced_app(exporter: SpanExporter) -> FastAPI:
    handle = configure_tracing(
        TracingConfig(service_name="test-service"),
        exporter=exporter,
        set_global=False,
    )
    assert handle is not None
    app = FastAPI()

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("handler failed")

    instrument_app(app, handle)
    return app


def test_request_creates_a_server_span():
    """Every public endpoint request produces a server span."""
    exporter = InMemorySpanExporter()
    app = _traced_app(exporter)

    with TestClient(app) as client:
        response = client.get("/ping")

    spans = exporter.get_finished_spans()
    assert response.status_code == 200
    assert len(spans) == 1
    span = spans[0]
    assert span.name == "GET /ping"
    assert span.attributes["service.name"] == "test-service"
    assert span.attributes["http.request.method"] == "GET"
    assert span.attributes["http.response.status_code"] == 200


def test_w3c_trace_context_is_propagated():
    """An upstream traceparent is adopted rather than replaced."""
    exporter = InMemorySpanExporter()
    app = _traced_app(exporter)
    trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    parent_span_id = "00f067aa0ba902b7"

    with TestClient(app) as client:
        client.get(
            "/ping",
            headers={"traceparent": f"00-{trace_id}-{parent_span_id}-01"},
        )

    span = exporter.get_finished_spans()[0]
    assert span.context is not None
    assert span.context.trace_id == int(trace_id, 16)
    assert span.parent is not None
    assert span.parent.span_id == int(parent_span_id, 16)


def test_unreachable_exporter_does_not_fail_requests():
    """A failing collector degrades observability, not availability."""

    class FailingExporter(SpanExporter):
        def export(self, spans):  # noqa: ANN001 - SDK signature
            raise RuntimeError("collector unreachable")

        def shutdown(self) -> None:
            return None

        def force_flush(self, timeout_millis: int = 30000) -> bool:
            return True

    exporter = FailingExporter()
    app = _traced_app(exporter)

    with TestClient(app) as client:
        response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_handler_errors_are_recorded_on_the_span():
    """An exception marks the span as failed and keeps the error type."""
    exporter = InMemorySpanExporter()
    app = _traced_app(exporter)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 500
    span = exporter.get_finished_spans()[0]
    assert span.status.status_code.name == "ERROR"
    assert span.attributes["error.type"] == "RuntimeError"


@pytest.mark.parametrize(
    ("directory", "module_name"),
    [
        ("auth-service", "auth_service"),
        ("crm-service", "crm_service"),
        ("billing-service", "billing_service"),
        ("inventory-service", "inventory_service"),
    ],
)
def test_each_service_exposes_a_traced_app(directory: str, module_name: str):
    """All four service packages wire the tracing middleware into their app."""
    module_path = (
        REPO_ROOT / "services" / directory / "src" / module_name / "__init__.py"
    )
    spec = importlib.util.spec_from_file_location(
        f"{module_name}_under_test", module_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    app = module.create_service_app(directory)
    assert app.state.tracing is not None

    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 200


def test_tracing_can_be_disabled():
    """A disabled configuration returns no handle and no middleware."""
    config = TracingConfig(service_name="disabled", enabled=False)
    assert configure_tracing(config, set_global=False) is None


def test_export_result_value_is_available_for_custom_exporters():
    """A successful custom exporter reports success through the SDK."""
    exporter = InMemorySpanExporter()
    app = _traced_app(exporter)
    with TestClient(app) as client:
        client.get("/ping")
    assert exporter.export(exporter.get_finished_spans()) == SpanExportResult.SUCCESS
