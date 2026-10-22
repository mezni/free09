"""Observability API endpoints (FR-050–FR-054, TM125–TM145)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, field_validator

from src.middleware.logging import LokiShipper, log_buffer, query_log_entries
from src.services.alerting import Alert, alert_router
from src.services.anomaly_detection import Anomaly, anomaly_detector
from src.services.runbooks import (
    Runbook,
    RunbookStep,
    UnknownServiceError,
    runbook_store,
)


class LogSearchRequest(BaseModel):
    """Request body for ``POST /search-logs``."""

    query: str = Field(min_length=1, max_length=1000)
    time_range: str | None = None
    limit: int = Field(default=100, ge=1, le=1000)


class LogEntryRead(BaseModel):
    """A structured log entry returned by the search API."""

    log_entry_id: str
    service: str
    level: str
    message: str
    timestamp: datetime
    request_id: str | None = None
    trace_id: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class LogFlushResponse(BaseModel):
    """Outcome of shipping buffered logs to Loki."""

    shipped: int
    buffered: int
    error: str | None = None


class AnomalyObservationRequest(BaseModel):
    """A metric observation submitted for anomaly detection."""

    metric: str = Field(min_length=1, max_length=200)
    value: float


class AnomalyRead(BaseModel):
    """An anomaly returned by the detector."""

    anomaly_id: str
    metric: str
    observed_value: float
    baseline: float
    score: float
    detected_at: datetime


class AlertRead(BaseModel):
    """An alert returned by the router."""

    alert_id: str
    alertname: str
    severity: str
    team: str
    labels: dict[str, str]
    annotations: dict[str, str]
    status: str
    started_at: datetime
    updated_at: datetime


class AnomalyDetectionResponse(BaseModel):
    """Result of one observation."""

    anomaly: AnomalyRead | None
    alert: AlertRead | None = None
    channels: list[str] = Field(default_factory=list)
    warning: str | None = None


class RunbookStepInput(BaseModel):
    """A runbook step supplied by a client."""

    order: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    action: str = Field(min_length=1, max_length=2000)
    expected: str = Field(min_length=1, max_length=2000)

    def to_step(self) -> RunbookStep:
        """Convert the input model to a domain step."""
        return RunbookStep(
            order=self.order,
            title=self.title,
            action=self.action,
            expected=self.expected,
        )


class RunbookCreateRequest(BaseModel):
    """Request body for creating a runbook."""

    title: str = Field(min_length=1, max_length=200)
    scenario: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    steps: list[RunbookStepInput] = Field(min_length=1)

    @field_validator("steps")
    @classmethod
    def _unique_orders(cls, steps: list[RunbookStepInput]) -> list[RunbookStepInput]:
        orders = [step.order for step in steps]
        if len(orders) != len(set(orders)):
            raise ValueError("step order values must be unique")
        return steps


class RunbookUpdateRequest(BaseModel):
    """Request body for updating a runbook."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    scenario: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=100)
    steps: list[RunbookStepInput] | None = Field(default=None, min_length=1)


class RunbookStepRead(BaseModel):
    """A runbook step returned by the API."""

    order: int
    title: str
    action: str
    expected: str
    status: str = "ready"


class RunbookRead(BaseModel):
    """A runbook returned by the API."""

    runbook_id: str
    title: str
    scenario: str
    steps: list[RunbookStepRead]
    author: str
    updated_at: datetime


class RunbookExecuteRequest(BaseModel):
    """Request body for executing a runbook."""

    target_service: str | None = Field(default=None, max_length=100)


def search_logs(payload: LogSearchRequest) -> list[LogEntryRead]:
    """Search buffered logs using a Loki-style query."""
    try:
        entries = query_log_entries(
            log_buffer,
            payload.query,
            time_range=payload.time_range,
            limit=payload.limit,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    return [LogEntryRead(**entry.as_dict()) for entry in entries]


def flush_logs() -> LogFlushResponse:
    """Attempt to ship buffered logs to Loki."""
    result = log_buffer.flush(LokiShipper.from_env())
    return LogFlushResponse(
        shipped=result.shipped,
        buffered=result.buffered,
        error=result.error,
    )


def observe_metric(payload: AnomalyObservationRequest) -> AnomalyDetectionResponse:
    """Observe a metric and route an alert when it is anomalous."""
    anomaly = anomaly_detector.observe(payload.metric, payload.value)
    if anomaly is None:
        return AnomalyDetectionResponse(anomaly=None)
    alert, _, channels, warning = alert_router.record(
        "performance_anomaly_detected",
        {
            "severity": "warning",
            "team": "platform",
            "metric": payload.metric,
        },
        {
            "summary": f"{payload.metric} deviated from its rolling baseline",
            "observed_value": str(payload.value),
            "baseline": str(anomaly.baseline),
        },
    )
    return AnomalyDetectionResponse(
        anomaly=_anomaly_read(anomaly),
        alert=_alert_read(alert),
        channels=channels,
        warning=warning,
    )


def list_anomalies(limit: int = 100) -> list[AnomalyRead]:
    """Return recent anomalies."""
    return [_anomaly_read(anomaly) for anomaly in anomaly_detector.recent(limit)]


def list_alerts(status_filter: str | None = None) -> list[AlertRead]:
    """Return alerts, optionally filtered by status."""
    return [_alert_read(alert) for alert in alert_router.list_alerts(status_filter)]


def resolve_alert(alert_id: str) -> AlertRead:
    """Resolve an alert."""
    alert = alert_router.resolve(alert_id)
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"alert '{alert_id}' was not found",
        )
    return _alert_read(alert)


def list_runbooks() -> list[RunbookRead]:
    """Return all runbooks."""
    return [_runbook_read(runbook) for runbook in runbook_store.list_runbooks()]


def get_runbook(runbook_id: str) -> RunbookRead:
    """Return one runbook."""
    runbook = runbook_store.get(runbook_id)
    if runbook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"runbook '{runbook_id}' was not found",
        )
    return _runbook_read(runbook)


def create_runbook(payload: RunbookCreateRequest) -> RunbookRead:
    """Create a runbook."""
    runbook = runbook_store.create(
        title=payload.title,
        scenario=payload.scenario,
        steps=[step.to_step() for step in payload.steps],
        author=payload.author,
    )
    return _runbook_read(runbook)


def update_runbook(runbook_id: str, payload: RunbookUpdateRequest) -> RunbookRead:
    """Update a runbook."""
    steps = (
        [step.to_step() for step in payload.steps]
        if payload.steps is not None
        else None
    )
    runbook = runbook_store.update(
        runbook_id,
        title=payload.title,
        scenario=payload.scenario,
        steps=steps,
        author=payload.author,
    )
    if runbook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"runbook '{runbook_id}' was not found",
        )
    return _runbook_read(runbook)


def execute_runbook(
    runbook_id: str,
    payload: RunbookExecuteRequest,
) -> dict[str, Any]:
    """Execute a runbook for a target service."""
    try:
        result = runbook_store.execute(
            runbook_id,
            target_service=payload.target_service,
            available_services={
                "auth-service",
                "crm-service",
                "billing-service",
                "notification-service",
            },
        )
    except UnknownServiceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"runbook '{runbook_id}' was not found",
        )
    return result


def _alert_read(alert: Alert) -> AlertRead:
    return AlertRead(**alert.as_dict())


def _anomaly_read(anomaly: Anomaly) -> AnomalyRead:
    return AnomalyRead(**anomaly.as_dict())


def _runbook_read(runbook: Runbook) -> RunbookRead:
    return RunbookRead(**runbook.as_dict())


__all__ = [
    "AlertRead",
    "AnomalyDetectionResponse",
    "AnomalyObservationRequest",
    "AnomalyRead",
    "LogEntryRead",
    "LogFlushResponse",
    "LogSearchRequest",
    "RunbookCreateRequest",
    "RunbookExecuteRequest",
    "RunbookRead",
    "RunbookStepInput",
    "RunbookStepRead",
    "RunbookUpdateRequest",
    "create_runbook",
    "execute_runbook",
    "flush_logs",
    "get_runbook",
    "list_alerts",
    "list_anomalies",
    "list_runbooks",
    "observe_metric",
    "resolve_alert",
    "search_logs",
    "update_runbook",
]
