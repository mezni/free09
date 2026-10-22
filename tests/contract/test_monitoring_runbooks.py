"""Incident runbook tests (FR-054, TM140–TM142)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.runbooks import RunbookStore, UnknownServiceError

pytestmark = [pytest.mark.contract, pytest.mark.runbook]

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = (
    "service-error-rate.md",
    "latency-spike.md",
    "database-connection-failure.md",
)


def test_documented_runbooks_cover_common_incidents():
    """Each documented runbook has steps, verification and escalation."""
    directory = REPO_ROOT / "docs/runbooks"
    for name in SCENARIOS:
        content = (directory / name).read_text()
        assert content.startswith("# Runbook:")
        assert "## Steps" in content
        assert "## Verification" in content
        assert "## Escalation" in content
        assert content.count("\n1.") >= 1


def test_seeded_runbooks_and_crud_api():
    """The store and API expose the three seeded procedures and accept edits."""
    store = RunbookStore()
    assert len(store.list_runbooks()) == 3

    with TestClient(app) as client:
        runbooks = client.get("/api/v1/runbooks")
        assert runbooks.status_code == 200
        assert len(runbooks.json()) == 3

        created = client.post(
            "/api/v1/runbooks",
            json={
                "title": "Cache eviction storm",
                "scenario": "cache_eviction",
                "author": "platform",
                "steps": [
                    {
                        "order": 1,
                        "title": "Inspect",
                        "action": "Check eviction metrics.",
                        "expected": "The cache is identified.",
                    }
                ],
            },
        )
        assert created.status_code == 201
        runbook_id = created.json()["runbook_id"]

        updated = client.patch(
            f"/api/v1/runbooks/{runbook_id}",
            json={"title": "Cache eviction storm v2"},
        )
        assert updated.status_code == 200
        assert updated.json()["title"] == "Cache eviction storm v2"

        fetched = client.get(f"/api/v1/runbooks/{runbook_id}")
        assert fetched.json()["title"] == "Cache eviction storm v2"


def test_runbook_execution_validates_target_service():
    """Execution succeeds for a real service and rejects an unknown one."""
    store = RunbookStore()
    runbook_id = store.list_runbooks()[0].runbook_id
    result = store.execute(
        runbook_id,
        target_service="auth-service",
        available_services={"auth-service", "crm-service"},
    )
    assert result is not None
    assert result["status"] == "completed"
    assert len(result["steps"]) >= 3

    with pytest.raises(UnknownServiceError, match="ghost-service"):
        store.execute(
            runbook_id,
            target_service="ghost-service",
            available_services={"auth-service", "crm-service"},
        )

    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/runbooks/{runbook_id}/execute",
            json={"target_service": "ghost-service"},
        )
    assert response.status_code == 409
