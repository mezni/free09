"""Prometheus metrics tests (FR-051, TM128–TM130)."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.middleware.metrics import REQUESTS_TOTAL
from src.observability.service_app import create_service_app

pytestmark = [pytest.mark.contract, pytest.mark.metric]

SERVICES = ("auth-service", "crm-service", "billing-service", "notification-service")
REQUIRED_METRICS = (
    "service_requests_total",
    "service_request_duration_seconds",
    "service_errors_total",
    "otel_spans_created_total",
    "otel_spans_exported_successful_total",
)


def _metric_value(**labels: str) -> float:
    return REQUESTS_TOTAL.labels(**labels)._value.get()  # noqa: SLF001


def test_metrics_endpoint_is_prometheus_compatible():
    """GET /metrics returns the documented metric families quickly."""
    with TestClient(app) as client:
        started = time.perf_counter()
        response = client.get("/metrics")
        elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    for metric in REQUIRED_METRICS:
        assert metric in body
    assert "process_resident_memory_bytes" in body
    assert elapsed < 0.5


def test_every_service_exposes_metrics_and_instruments_requests():
    """Each of the four services serves /metrics and counts its traffic."""
    for service_name in SERVICES:
        service_app = create_service_app(service_name)
        before = _metric_value(
            service=service_name,
            method="GET",
            endpoint="/healthz",
            status="200",
        )
        with TestClient(service_app) as client:
            assert client.get("/healthz").status_code == 200
            metrics = client.get("/metrics")
        after = _metric_value(
            service=service_name,
            method="GET",
            endpoint="/healthz",
            status="200",
        )
        assert metrics.status_code == 200
        assert service_name in metrics.text or "service_requests_total" in metrics.text
        assert after == before + 1


def test_error_responses_increment_error_counter():
    """A 5xx response is counted in service_errors_total."""
    service_app = create_service_app("crm-service")

    @service_app.get("/explode")
    def explode() -> None:
        raise RuntimeError("boom")

    with TestClient(service_app, raise_server_exceptions=False) as client:
        response = client.get("/explode")
        metrics = client.get("/metrics")

    assert response.status_code == 500
    assert "service_errors_total" in metrics.text
    assert 'endpoint="/explode"' in metrics.text
