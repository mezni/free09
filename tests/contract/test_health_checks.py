"""Liveness and readiness probe tests (FR-042, TM110–TM112)."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

import src.main as main_module
from src.main import app

pytestmark = [pytest.mark.unit, pytest.mark.health]


def test_liveness_probe_is_healthy():
    """The liveness probe reports a running process."""
    with TestClient(app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_probe_reports_dependencies():
    """Readiness reports the database state and never returns a bare 5xx."""
    with TestClient(app) as client:
        response = client.get("/readyz")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "healthy"
    assert body["services"]["postgres"] == "healthy"


def test_health_alias_matches_readiness():
    """The non-versioned /health alias is the readiness contract."""
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_failure_does_not_restart_the_process(
    monkeypatch: pytest.MonkeyPatch,
):
    """A down database reports not-ready while liveness stays healthy."""
    monkeypatch.setattr(main_module, "database_ready", lambda: False)
    with TestClient(app) as client:
        liveness = client.get("/healthz")
        readiness = client.get("/readyz")

    assert liveness.status_code == 200
    assert readiness.status_code == 503
    assert readiness.json()["status"] == "unhealthy"
    assert readiness.json()["services"]["postgres"] == "unhealthy"


def test_probes_respond_under_one_hundred_milliseconds():
    """The health endpoints meet NFR-022."""
    with TestClient(app) as client:
        for path in ("/healthz", "/readyz"):
            durations = []
            for _ in range(5):
                started = time.perf_counter()
                response = client.get(path)
                durations.append((time.perf_counter() - started) * 1000.0)
                assert response.status_code == 200
            assert max(durations) < 100.0, (path, durations)
