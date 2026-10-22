"""Trace propagation, mesh telemetry and dashboard tests (FR-055–FR-056)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.middleware.metrics import MESH_FALLBACK_TOTAL, record_mesh_fallback
from src.observability.tracing import (
    TracingConfig,
    configure_tracing,
    instrument_app,
    outgoing_trace_headers,
)

pytestmark = [pytest.mark.contract, pytest.mark.trace, pytest.mark.mesh]

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736"
PARENT_SPAN_ID = "00f067aa0ba902b7"


def test_outbound_headers_inject_active_trace_context():
    """Outbound calls carry the same trace ID as the inbound request."""
    app = FastAPI()
    handle = configure_tracing(
        TracingConfig(service_name="auth-service"), set_global=False
    )
    assert handle is not None

    @app.get("/call")
    def call() -> dict[str, str]:
        return outgoing_trace_headers({"traceparent": "upstream"})

    instrument_app(app, handle)
    with TestClient(app) as client:
        response = client.get(
            "/call",
            headers={"traceparent": f"00-{TRACE_ID}-{PARENT_SPAN_ID}-01"},
        )

    headers = response.json()
    assert re.match(
        rf"^00-{TRACE_ID}-[0-9a-f]{{16}}-[0-9a-f]{{2}}$", headers["traceparent"]
    )
    assert headers["traceparent"] != "upstream"


def test_prometheus_scrapes_all_services_and_istio_sidecars():
    """Prometheus discovers the four services plus mesh sidecar metrics."""
    config = yaml.safe_load(
        (REPO_ROOT / "deploy/prometheus/prometheus.yml").read_text()
    )
    assert config["global"]["scrape_interval"] == "15s"
    jobs = {job["job_name"]: job for job in config["scrape_configs"]}
    for service in (
        "auth-service",
        "crm-service",
        "billing-service",
        "notification-service",
    ):
        assert jobs[service]["metrics_path"] == "/metrics"
        assert jobs[service]["static_configs"][0]["targets"] == [f"{service}:8000"]
    assert jobs["istio-proxies"]["metrics_path"] == "/stats/prometheus"
    assert "/etc/prometheus/alerts.yml" in config["rule_files"]


def test_istio_telemetry_enables_metrics_and_tracing():
    """Istio Telemetry resource advertises Prometheus and OTLP providers."""
    telemetry = yaml.safe_load((REPO_ROOT / "deploy/istio/telemetry.yaml").read_text())
    assert telemetry["kind"] == "Telemetry"
    assert telemetry["spec"]["metrics"][0]["providers"] == [{"name": "prometheus"}]
    tracing = telemetry["spec"]["tracing"][0]
    assert tracing["providers"] == [{"name": "opentelemetry"}]
    assert tracing["randomSamplingPercentage"] == 100


def test_grafana_dashboard_covers_critical_service_paths():
    """The provisioned dashboard contains all four services and latency."""
    dashboard = json.loads(
        (REPO_ROOT / "deploy/grafana/dashboards/telco-services.json").read_text()
    )
    titles = " ".join(panel["title"] for panel in dashboard["panels"])
    for service in (
        "auth-service",
        "crm-service",
        "billing-service",
        "notification-service",
    ):
        assert service in titles
    assert "p95 latency" in titles


def test_mesh_fallback_is_recorded():
    """A missing sidecar increments the documented fallback metric."""
    before = MESH_FALLBACK_TOTAL.labels(
        service="auth-service", reason="sidecar_unavailable"
    )._value.get()  # noqa: SLF001
    record_mesh_fallback("auth-service")
    after = MESH_FALLBACK_TOTAL.labels(
        service="auth-service", reason="sidecar_unavailable"
    )._value.get()  # noqa: SLF001
    assert after == before + 1
