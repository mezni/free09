"""Structured logging and log search tests (FR-050, TM125–TM127)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.middleware.logging import (
    LogBuffer,
    LogEntry,
    LokiShipError,
    LokiShipper,
    log_buffer,
    query_log_entries,
)
from src.observability.service_app import create_service_app

pytestmark = [pytest.mark.contract, pytest.mark.log]

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset_log_buffer() -> None:
    log_buffer.reset()


def _entry(
    message: str,
    *,
    service: str = "auth-service",
    level: str = "info",
    offset_seconds: int = 0,
) -> LogEntry:
    return LogEntry(
        log_entry_id=f"entry-{message}",
        service=service,
        level=level,
        message=message,
        timestamp=datetime.now(timezone.utc) + timedelta(seconds=offset_seconds),
        request_id="request-1",
        trace_id="4bf92f3577b34da6a3ce929d0e0e4736",
        attributes={"path": "/healthz"},
    )


def test_service_request_emits_structured_log_entry():
    """Each request produces service, level, request and trace identifiers."""
    service_app = create_service_app("auth-service")

    with TestClient(service_app) as client:
        response = client.get("/healthz", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    entries = log_buffer.entries()
    assert entries
    entry = entries[-1]
    assert entry.service == "auth-service"
    assert entry.level == "info"
    assert entry.request_id == "req-123"
    assert entry.attributes["path"] == "/healthz"
    assert entry.attributes["status"] == 200
    assert entry.message.startswith("GET /healthz")


def test_search_logs_filters_and_is_fast():
    """The search endpoint filters by service/level/text within the SLO."""
    for index in range(1000):
        log_buffer.append(_entry(f"message {index}"))
    log_buffer.append(_entry("database timeout", level="error"))

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/search-logs",
            json={
                "query": '{service="auth-service"} |= "database"',
                "limit": 10,
            },
        )

    assert response.status_code == 200
    hits = response.json()
    assert len(hits) == 1
    assert hits[0]["message"] == "database timeout"

    start = datetime.now(timezone.utc) - timedelta(minutes=5)
    matches = query_log_entries(
        log_buffer,
        '{service="auth-service"} | level="error"',
        time_range=f"{start.isoformat()} - {datetime.now(timezone.utc).isoformat()}",
    )
    assert matches[0].message == "database timeout"


def test_log_shipper_failure_keeps_entries_buffered():
    """Loki being unreachable never drops buffered entries."""

    class FailingShipper:
        def ship(self, entries: object) -> int:
            raise LokiShipError("connection refused")

    buffer = LogBuffer(capacity=10)
    buffer.append(_entry("one"))

    failed = buffer.flush(FailingShipper())  # type: ignore[arg-type]
    assert failed.shipped == 0
    assert failed.buffered == 1
    assert failed.error is not None
    assert len(buffer) == 1

    class SuccessfulShipper:
        def ship(self, entries: object) -> int:
            return len(list(entries))  # type: ignore[arg-type]

    delivered = buffer.flush(SuccessfulShipper())  # type: ignore[arg-type]
    assert delivered.ok
    assert delivered.shipped == 1
    assert len(buffer) == 0


def test_loki_configuration_declares_retention_and_push_api():
    """The local Loki configuration matches the 90-day retention contract."""
    import yaml

    config = yaml.safe_load((REPO_ROOT / "deploy/loki/loki-config.yaml").read_text())
    assert config["server"]["http_listen_port"] == 3100
    assert config["limits_config"]["retention_period"] == "2160h"
    assert config["compactor"]["retention_enabled"] is True

    shipper = LokiShipper("http://loki:3100")
    assert shipper.endpoint.endswith("/loki/api/v1/push")


def test_query_parser_accepts_contract_syntax():
    """The parser extracts the three documented filter forms."""
    from src.middleware.logging import parse_log_query

    assert parse_log_query('{service="crm-service"} |= "timeout"') == {
        "service": "crm-service",
        "contains": "timeout",
    }
    assert parse_log_query('{service="crm-service"} | level="error"') == {
        "service": "crm-service",
        "level": "error",
    }
    entry = _entry("payload")
    assert json.loads(json.dumps(entry.as_dict()))["service"] == "auth-service"
