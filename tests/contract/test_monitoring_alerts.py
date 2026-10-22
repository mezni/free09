"""Alert rules, routing and anomaly detection tests (FR-052–FR-053)."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from src.main import app
from src.services.alerting import AlertRouter, alert_router
from src.services.anomaly_detection import AnomalyDetector, anomaly_detector

pytestmark = [pytest.mark.contract, pytest.mark.alert, pytest.mark.anomaly]

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset_observability_state() -> None:
    alert_router.reset()
    anomaly_detector.reset()


def test_prometheus_rules_cover_required_alerts_and_labels():
    """Every required alert carries severity, team and a runbook link."""
    rules = yaml.safe_load((REPO_ROOT / "deploy/prometheus/alerts.yml").read_text())[
        "groups"
    ][0]["rules"]
    by_name = {rule["alert"]: rule for rule in rules}
    assert {
        "ServiceErrorRateHigh",
        "ServiceLatencyHigh",
        "ServiceDown",
        "PerformanceAnomalyDetected",
    } <= set(by_name)

    for name in ("ServiceErrorRateHigh", "ServiceLatencyHigh", "ServiceDown"):
        labels = by_name[name]["labels"]
        assert labels["severity"] in {"warning", "critical"}
        assert labels["team"] in {"backend", "platform", "database"}
    assert "runbook_url" in by_name["ServiceErrorRateHigh"]["annotations"]
    assert "PerformanceAnomalyDetected" in by_name


def test_alertmanager_routes_teams_and_severity():
    """Alertmanager configuration routes critical and team alerts."""
    config = yaml.safe_load(
        (REPO_ROOT / "deploy/alertmanager/alertmanager.yml").read_text()
    )
    assert config["route"]["group_by"] == ["alertname", "instance", "job"]
    assert config["route"]["repeat_interval"] == "4h"
    routes = config["route"]["routes"]
    assert any("severity" in str(route.get("matchers")) for route in routes)
    assert any("team" in str(route.get("matchers")) for route in routes)
    receivers = {receiver["name"] for receiver in config["receivers"]}
    assert {"team-alerts", "database-alerts", "pagerduty"} <= receivers


def test_router_routes_critical_to_pagerduty_and_deduplicates():
    """Critical alerts reach PagerDuty and repeats are deduplicated."""
    router = AlertRouter(repeat_interval=timedelta(hours=4))
    alert, duplicate, channels, warning = router.record(
        "ServiceErrorRateHigh",
        {"severity": "critical", "team": "backend", "service": "auth-service"},
        {"summary": "error rate"},
    )
    assert duplicate is False
    assert warning is None
    assert "pagerduty" in channels
    assert "email" in channels

    repeat, duplicate_again, _, _ = router.record(
        "ServiceErrorRateHigh",
        {"severity": "critical", "team": "backend", "service": "auth-service"},
    )
    assert duplicate_again is True
    assert repeat.alert_id == alert.alert_id
    assert router.resolve(alert.alert_id) is not None
    assert router.list_alerts("resolved")[0].alert_id == alert.alert_id


def test_anomaly_detector_flags_rolling_percentile_deviation():
    """A spike against a stable baseline produces an anomaly."""
    detector = AnomalyDetector(min_samples=5, threshold=3.5)
    for value in (100.0, 101.0, 99.0, 100.0, 100.0):
        assert detector.observe("latency_ms", value) is None
    anomaly = detector.observe("latency_ms", 1000.0)
    assert anomaly is not None
    assert anomaly.metric == "latency_ms"
    assert anomaly.score > 3.5
    assert detector.recent()[0].anomaly_id == anomaly.anomaly_id


def test_observation_endpoint_records_anomaly_alert():
    """The API turns an anomalous observation into a routed alert."""
    with TestClient(app) as client:
        for value in (100.0, 101.0, 99.0, 100.0, 100.0):
            response = client.post(
                "/api/v1/anomalies/observe",
                json={"metric": "latency_ms", "value": value},
            )
            assert response.status_code == 200
            assert response.json()["anomaly"] is None

        spike = client.post(
            "/api/v1/anomalies/observe",
            json={"metric": "latency_ms", "value": 1000.0},
        )
        alerts = client.get("/api/v1/alerts")

    payload = spike.json()
    assert payload["anomaly"]["metric"] == "latency_ms"
    assert payload["alert"]["alertname"] == "performance_anomaly_detected"
    assert "slack" in payload["channels"]
    assert any(
        alert["alertname"] == "performance_anomaly_detected" for alert in alerts.json()
    )
