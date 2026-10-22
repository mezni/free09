"""Webhook router (FR-044)."""

from fastapi import APIRouter, status

from src.api.endpoints.webhooks import (
    SubscriptionRequest,
    SubscriptionResponse,
    WebhookReceipt,
    get_event,
    list_events,
    receive_event,
    subscribe,
    unsubscribe,
)
from src.services.webhooks import WebhookEvent

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

router.add_api_route(
    "/subscribe",
    subscribe,
    methods=["POST"],
    response_model=SubscriptionResponse,
    summary="Subscribe to webhook events",
)
router.add_api_route(
    "/unsubscribe",
    unsubscribe,
    methods=["POST"],
    response_model=SubscriptionResponse,
    summary="Unsubscribe from webhook events",
)
router.add_api_route(
    "/event",
    receive_event,
    methods=["POST"],
    response_model=WebhookReceipt,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive and validate a webhook event",
)
router.add_api_route(
    "/events",
    list_events,
    methods=["GET"],
    response_model=list[WebhookEvent],
    summary="List webhook events",
)
router.add_api_route(
    "/events/{event_id}",
    get_event,
    methods=["GET"],
    response_model=WebhookEvent,
    summary="Get a webhook event",
)

__all__ = ["SubscriptionRequest", "router"]
