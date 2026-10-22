"""Observability router (FR-050–FR-054)."""

from fastapi import APIRouter, status

from src.api.endpoints.observability import (
    AlertRead,
    AnomalyDetectionResponse,
    AnomalyRead,
    LogEntryRead,
    LogFlushResponse,
    RunbookRead,
    create_runbook,
    execute_runbook,
    flush_logs,
    get_runbook,
    list_alerts,
    list_anomalies,
    list_runbooks,
    observe_metric,
    resolve_alert,
    search_logs,
    update_runbook,
)

router = APIRouter(tags=["observability"])

router.add_api_route(
    "/search-logs",
    search_logs,
    methods=["POST"],
    response_model=list[LogEntryRead],
    summary="Search structured logs",
)
router.add_api_route(
    "/logs/flush",
    flush_logs,
    methods=["POST"],
    response_model=LogFlushResponse,
    summary="Ship buffered logs to Loki",
)
router.add_api_route(
    "/alerts",
    list_alerts,
    methods=["GET"],
    response_model=list[AlertRead],
    summary="List alerts",
)
router.add_api_route(
    "/alerts/{alert_id}/resolve",
    resolve_alert,
    methods=["POST"],
    response_model=AlertRead,
    summary="Resolve an alert",
)
router.add_api_route(
    "/anomalies",
    list_anomalies,
    methods=["GET"],
    response_model=list[AnomalyRead],
    summary="List detected anomalies",
)
router.add_api_route(
    "/anomalies/observe",
    observe_metric,
    methods=["POST"],
    response_model=AnomalyDetectionResponse,
    summary="Observe a metric for anomalies",
)
router.add_api_route(
    "/runbooks",
    list_runbooks,
    methods=["GET"],
    response_model=list[RunbookRead],
    summary="List runbooks",
)
router.add_api_route(
    "/runbooks",
    create_runbook,
    methods=["POST"],
    response_model=RunbookRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a runbook",
)
router.add_api_route(
    "/runbooks/{runbook_id}",
    get_runbook,
    methods=["GET"],
    response_model=RunbookRead,
    summary="Get a runbook",
)
router.add_api_route(
    "/runbooks/{runbook_id}",
    update_runbook,
    methods=["PATCH"],
    response_model=RunbookRead,
    summary="Update a runbook",
)
router.add_api_route(
    "/runbooks/{runbook_id}/execute",
    execute_runbook,
    methods=["POST"],
    response_model=dict,
    summary="Execute a runbook",
)

__all__ = ["router"]
