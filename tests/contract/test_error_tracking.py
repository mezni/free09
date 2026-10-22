"""Centralized error-tracking tests (FR-041, TM107–TM109)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.observability.errors import (
    ErrorTracker,
    build_error_response,
)
from src.observability.service_app import create_service_app

pytestmark = [pytest.mark.unit, pytest.mark.error]


@pytest.fixture(autouse=True)
def _clear_errors():
    ErrorTracker.clear_errors()
    yield
    ErrorTracker.clear_errors()


def test_track_records_the_required_fields():
    """Every tracked error carries service, endpoint, type and request id."""
    error = ErrorTracker.track(
        service="crm-service",
        endpoint="/api/v1/customers",
        error_type="ValidationError",
        message="bad payload",
        request_id="req-123",
    )

    assert error.service == "crm-service"
    assert error.endpoint == "/api/v1/customers"
    assert error.error_type == "ValidationError"
    assert error.message == "bad payload"
    assert error.request_id == "req-123"
    assert error.error_id.startswith("err-")
    assert ErrorTracker.get_recent_errors(limit=1) == [error]


def test_buffer_is_bounded(monkeypatch: pytest.MonkeyPatch):
    """The buffer keeps the most recent errors only."""
    monkeypatch.setattr(ErrorTracker, "_max_buffer_size", 2)
    for index in range(4):
        ErrorTracker.track(
            service="svc",
            endpoint="/x",
            error_type="E",
            message=str(index),
        )
    messages = [error.message for error in ErrorTracker.get_recent_errors()]
    assert messages == ["2", "3"]


def test_canonical_error_envelope_has_the_contract_fields():
    """The error body matches the phase-5 error-response contract."""
    payload = build_error_response(
        code="VALIDATION_ERROR",
        message="invalid",
        request_id="req-1",
        service="crm-service",
    )
    assert set(payload) == {
        "error_id",
        "code",
        "message",
        "timestamp",
        "request_id",
        "service",
    }
    assert payload["code"] == "VALIDATION_ERROR"


def test_middleware_records_unhandled_exception_with_request_id():
    """The app records the request id set by the request-id middleware."""
    app = create_service_app("crm-service")

    @app.get("/explode")
    def explode() -> None:
        raise ValueError("boom")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/explode")

    assert response.status_code == 500
    errors = ErrorTracker.get_recent_errors()
    assert errors, "The middleware recorded no error"
    error = errors[-1]
    assert error.service == "crm-service"
    assert error.endpoint == "/explode"
    assert error.error_type == "ValueError"
    assert error.request_id


def test_app_returns_the_canonical_envelope_on_failure():
    """A failed request returns the error envelope rather than a bare 500."""
    app = create_service_app("billing-service")

    @app.get("/explode")
    def explode() -> None:
        raise RuntimeError("boom")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/explode")

    body = response.json()
    assert response.status_code == 500
    assert body["code"] == "INTERNAL_SERVER_ERROR"
    assert body["service"] == "billing-service"
    assert body["request_id"]
    assert body["request_id"] == ErrorTracker.get_recent_errors()[-1].request_id
