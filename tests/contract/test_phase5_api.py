"""API contract tests for the phase-5 endpoints (FR-042–FR-044)."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.api_keys import api_keys
from src.services.webhooks import signature_for, webhooks

pytestmark = [pytest.mark.contract]


@pytest.fixture(autouse=True)
def _reset_stores():
    api_keys.reset()
    webhooks.reset()
    yield
    api_keys.reset()
    webhooks.reset()


def test_openapi_declares_the_phase5_endpoints():
    """The contract layer documents every phase-5 endpoint."""
    schema = app.openapi()
    paths = schema["paths"]
    expected = {
        "/healthz",
        "/readyz",
        "/health",
        "/api/v1/api-keys",
        "/api/v1/api-keys/{prefix}",
        "/api/v1/webhooks/subscribe",
        "/api/v1/webhooks/unsubscribe",
        "/api/v1/webhooks/event",
    }
    assert expected <= set(paths)


def test_api_key_crud_contract():
    """The API key endpoints implement the documented CRUD surface."""
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/api-keys",
            json={"person_id": "person-1", "scopes": ["read", "write"]},
        )
        assert created.status_code == 201
        body = created.json()
        assert body["key"].startswith(f"{body['prefix']}.")
        assert body["scopes"] == ["read", "write"]

        listed = client.get("/api/v1/api-keys", params={"person_id": "person-1"})
        assert listed.status_code == 200
        assert [key["prefix"] for key in listed.json()] == [body["prefix"]]

        fetched = client.get(f"/api/v1/api-keys/{body['prefix']}")
        assert fetched.status_code == 200
        assert fetched.json()["person_id"] == "person-1"

        patched = client.patch(
            f"/api/v1/api-keys/{body['prefix']}",
            json={"is_active": False, "scopes": ["read"]},
        )
        assert patched.status_code == 200
        assert patched.json()["is_active"] is False
        assert patched.json()["scopes"] == ["read"]

        deleted = client.delete(f"/api/v1/api-keys/{body['prefix']}")
        assert deleted.status_code == 204


def test_api_key_rejects_an_unknown_scope():
    """Unknown scopes are a 400, not a silent grant."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/api-keys",
            json={"person_id": "person-1", "scopes": ["superuser"]},
        )
    assert response.status_code == 400


def test_webhook_endpoint_validates_and_delivers(
    monkeypatch: pytest.MonkeyPatch,
):
    """A signed event is accepted, delivered and deduplicated."""
    secret = "contract-secret"
    monkeypatch.setenv("TELECO_WEBHOOK_SECRET", secret)
    received: list[dict] = []
    webhooks.register("person.created")(received.append)

    payload = {"event_type": "person.created", "id": "person-1"}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature_for(body, secret),
        "Idempotency-Key": "delivery-1",
    }

    with TestClient(app) as client:
        first = client.post("/api/v1/webhooks/event", content=body, headers=headers)
        second = client.post("/api/v1/webhooks/event", content=body, headers=headers)

    assert first.status_code == 202
    assert first.json()["event"]["status"] == "delivered"
    assert first.json()["duplicate"] is False
    assert second.status_code == 202
    assert second.json()["duplicate"] is True
    assert len(received) == 1


def test_webhook_endpoint_rejects_an_invalid_signature(
    monkeypatch: pytest.MonkeyPatch,
):
    """A bad signature is a 401 and does not reach a handler."""
    monkeypatch.setenv("TELECO_WEBHOOK_SECRET", "contract-secret")
    received: list[dict] = []
    webhooks.register("person.created")(received.append)
    body = b'{"event_type":"person.created","id":"person-1"}'

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/webhooks/event",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Signature": "sha256=invalid",
            },
        )

    assert response.status_code == 401
    assert received == []


def test_webhook_subscription_contract():
    """Subscribe and unsubscribe accept the known event set."""
    with TestClient(app) as client:
        subscribed = client.post(
            "/api/v1/webhooks/subscribe",
            json={"event_types": ["person.created"]},
        )
        assert subscribed.status_code == 200
        assert subscribed.json()["event_types"] == ["person.created"]

        unsubscribed = client.post(
            "/api/v1/webhooks/unsubscribe",
            json={"event_types": ["person.created"]},
        )
        assert unsubscribed.status_code == 200
        assert unsubscribed.json()["event_types"] == []
