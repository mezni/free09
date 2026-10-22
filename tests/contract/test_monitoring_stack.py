"""Local monitoring stack wiring tests (FR-050–FR-056)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.contract, pytest.mark.metric, pytest.mark.log]

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_observability_overlay_contains_full_stack():
    """The overlay adds Loki, Prometheus, Alertmanager, Grafana and Jaeger."""
    overlay = yaml.safe_load(
        (REPO_ROOT / "deploy/compose/observability.yaml").read_text()
    )
    services = overlay["services"]
    assert {"jaeger", "loki", "prometheus", "alertmanager", "grafana"} <= set(services)
    assert services["loki"]["ports"] == ["127.0.0.1:3100:3100"]
    assert services["prometheus"]["ports"] == ["127.0.0.1:9090:9090"]
    assert services["alertmanager"]["ports"] == ["127.0.0.1:9093:9093"]
    assert services["grafana"]["ports"] == ["127.0.0.1:3000:3000"]


def test_monitoring_configuration_files_parse():
    """Every provisioned monitoring configuration is valid YAML."""
    for relative in (
        "deploy/loki/loki-config.yaml",
        "deploy/prometheus/prometheus.yml",
        "deploy/prometheus/alerts.yml",
        "deploy/alertmanager/alertmanager.yml",
        "deploy/grafana/provisioning/datasources/datasources.yaml",
        "deploy/grafana/provisioning/dashboards/dashboards.yaml",
        "deploy/istio/telemetry.yaml",
    ):
        document = yaml.safe_load((REPO_ROOT / relative).read_text())
        assert document is not None
