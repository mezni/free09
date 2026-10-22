"""Webhook subscription, validation and delivery endpoints (FR-044)."""

from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, Field

from src.services.webhooks import (
    InvalidSignatureError,
    UnknownEventError,
    WebhookEvent,
    WebhookEventNotFoundError,
    WebhookSecretError,
    webhooks,
)

SIGNATURE_HEADERS = ("x-webhook-signature", "x-hub-signature-256")


class SubscriptionRequest(BaseModel):
    """Request body for subscribing or unsubscribing."""

    event_types: list[str] = Field(min_length=1)


class SubscriptionResponse(BaseModel):
    """Confirmation of the current outbound subscriptions."""

    event_types: list[str]


class WebhookReceipt(BaseModel):
    """Response returned for a received webhook event."""

    event: WebhookEvent
    duplicate: bool = False


def subscribe(payload: SubscriptionRequest) -> SubscriptionResponse:
    """Subscribe the platform to one or more event types."""
    try:
        current = webhooks.subscribe(payload.event_types)
    except UnknownEventError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    return SubscriptionResponse(event_types=sorted(current))


def unsubscribe(payload: SubscriptionRequest) -> SubscriptionResponse:
    """Remove outbound subscriptions."""
    try:
        current = webhooks.unsubscribe(payload.event_types)
    except UnknownEventError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    return SubscriptionResponse(event_types=sorted(current))


async def receive_event(request: Request) -> WebhookReceipt:
    """Validate an inbound event before dispatching it to a handler."""
    raw_body = await request.body()
    try:
        payload: dict[str, Any] = json.loads(raw_body or b"{}")
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook body is not valid JSON",
        ) from error

    event_type = payload.get("event_type") or payload.get("type")
    if not isinstance(event_type, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook body must carry an event_type",
        )

    signature = None
    for header in SIGNATURE_HEADERS:
        value = request.headers.get(header)
        if value:
            signature = value
            break

    try:
        event, duplicate = webhooks.process(
            event_type=event_type,
            payload=payload,
            signature=signature,
            idempotency_key=request.headers.get("Idempotency-Key"),
            raw_body=raw_body,
        )
    except WebhookSecretError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)
        ) from error
    except InvalidSignatureError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        ) from error
    except UnknownEventError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error

    return WebhookReceipt(event=event, duplicate=duplicate)


def get_event(event_id: str) -> WebhookEvent:
    """Return the delivery history for one event."""
    try:
        return webhooks.get(event_id)
    except WebhookEventNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook event '{event_id}' was not found",
        ) from error


def list_events(limit: int = 50) -> list[WebhookEvent]:
    """Return the most recent webhook events."""
    return webhooks.list(limit=limit)


__all__ = [
    "SubscriptionRequest",
    "SubscriptionResponse",
    "WebhookReceipt",
    "get_event",
    "list_events",
    "receive_event",
    "subscribe",
    "unsubscribe",
]
