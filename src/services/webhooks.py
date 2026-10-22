"""Webhook signature validation, idempotency and delivery (FR-044).

The processor implements the phase-5 contract:

* a delivery without a valid HMAC signature is rejected before any handler
  runs, and is never retried;
* a repeated idempotency key is acknowledged but processed only once;
* a handler that raises is retried until it succeeds or the attempt budget is
  exhausted, so delivery is at-least-once rather than at-most-once.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

KNOWN_EVENTS: frozenset[str] = frozenset(
    {
        "person.created",
        "person.updated",
        "person.deleted",
        "api_key.created",
    }
)

WebhookHandler = Callable[[dict[str, Any]], None]


class WebhookError(Exception):
    """Base class for webhook processing failures."""


class InvalidSignatureError(WebhookError):
    """The delivery signature is missing or does not match the payload."""


class UnknownEventError(WebhookError):
    """The event type is not part of the platform contract."""


class WebhookSecretError(WebhookError):
    """No webhook signing secret is configured, so validation cannot run."""


class WebhookEventNotFoundError(KeyError):
    """No event matches the supplied identifier."""


class WebhookDelivery(BaseModel):
    """One delivery attempt for an event."""

    delivery_id: str
    event_id: str
    attempt_number: int
    status: str
    response_code: int | None = None
    error: str | None = None
    attempted_at: str


class WebhookEvent(BaseModel):
    """A validated event and its delivery history."""

    event_id: str
    event_type: str
    payload: dict[str, Any]
    status: str
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    idempotency_key: str | None = None
    created_at: str
    updated_at: str | None = None
    deliveries: list[WebhookDelivery] = Field(default_factory=list)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def signature_for(payload: bytes, secret: str) -> str:
    """Return the `sha256=<hex>` signature for a payload."""
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_signature(payload: bytes, signature: str | None, secret: str) -> bool:
    """Compare a presented signature in constant time."""
    if not signature:
        return False
    return hmac.compare_digest(signature_for(payload, secret), signature)


def _secret_from_env() -> str | None:
    secret = os.environ.get("TELECO_WEBHOOK_SECRET", "").strip()
    return secret or None


def _serialize(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class WebhookProcessor:
    """Thread-safe event registry, retry loop and idempotency store."""

    def __init__(
        self,
        *,
        secret_provider: Callable[[], str | None] = _secret_from_env,
        max_attempts: int = 3,
    ) -> None:
        self._secret_provider = secret_provider
        self._max_attempts = max_attempts
        self._handlers: dict[str, list[WebhookHandler]] = {}
        self._subscriptions: set[str] = set()
        self._events: dict[str, WebhookEvent] = {}
        self._idempotency: dict[str, str] = {}
        self._lock = threading.RLock()

    def reset(self) -> None:
        """Remove handlers, events and idempotency records (used by tests)."""
        with self._lock:
            self._handlers.clear()
            self._subscriptions.clear()
            self._events.clear()
            self._idempotency.clear()

    def register(self, event_type: str) -> Callable[[WebhookHandler], WebhookHandler]:
        """Register a handler for an event type."""
        self._validate_event(event_type)

        def decorator(handler: WebhookHandler) -> WebhookHandler:
            with self._lock:
                self._handlers.setdefault(event_type, []).append(handler)
            return handler

        return decorator

    def subscribe(self, event_types: list[str]) -> set[str]:
        """Subscribe the platform to outbound event types."""
        for event_type in event_types:
            self._validate_event(event_type)
        with self._lock:
            self._subscriptions.update(event_types)
            return set(self._subscriptions)

    def unsubscribe(self, event_types: list[str]) -> set[str]:
        """Remove outbound subscriptions."""
        for event_type in event_types:
            self._validate_event(event_type)
        with self._lock:
            self._subscriptions.difference_update(event_types)
            return set(self._subscriptions)

    def subscriptions(self) -> set[str]:
        """Return the current outbound subscriptions."""
        with self._lock:
            return set(self._subscriptions)

    def process(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
        signature: str | None,
        idempotency_key: str | None = None,
        raw_body: bytes | None = None,
    ) -> tuple[WebhookEvent, bool]:
        """Validate and deliver an event.

        Returns:
            The event and a flag that is True when an idempotency key
            suppressed a duplicate delivery.

        Raises:
            WebhookSecretError: No secret is configured.
            InvalidSignatureError: The signature is absent or wrong.
            UnknownEventError: The event type is not defined.
        """
        secret = self._secret_provider()
        if not secret:
            raise WebhookSecretError("TELECO_WEBHOOK_SECRET is not configured")

        body = raw_body if raw_body is not None else _serialize(payload)
        if not verify_signature(body, signature, secret):
            raise InvalidSignatureError("Webhook signature is missing or invalid")

        self._validate_event(event_type)

        with self._lock:
            if idempotency_key and idempotency_key in self._idempotency:
                return self._events[self._idempotency[idempotency_key]], True

        handlers = self._handlers.get(event_type, [])
        if not handlers:
            raise UnknownEventError(f"No handler registered for event: {event_type}")

        event = WebhookEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            payload=payload,
            status="pending",
            max_delivery_attempts=self._max_attempts,
            idempotency_key=idempotency_key,
            created_at=_now(),
        )

        delivered = False
        for attempt in range(1, self._max_attempts + 1):
            error_message: str | None = None
            try:
                for handler in handlers:
                    handler(payload)
            except Exception as error:  # noqa: BLE001 - handler failures are data
                error_message = f"{type(error).__name__}: {error}"
            event.deliveries.append(
                WebhookDelivery(
                    delivery_id=str(uuid4()),
                    event_id=event.event_id,
                    attempt_number=attempt,
                    status="failed" if error_message else "success",
                    response_code=500 if error_message else 200,
                    error=error_message,
                    attempted_at=_now(),
                )
            )
            event.delivery_attempts = attempt
            if error_message is None:
                delivered = True
                break

        event.status = "delivered" if delivered else "failed"
        event.updated_at = _now()

        with self._lock:
            self._events[event.event_id] = event
            if idempotency_key:
                self._idempotency[idempotency_key] = event.event_id
        return event, False

    def retry(self, event_id: str) -> WebhookEvent:
        """Retry a failed event, preserving its delivery history."""
        with self._lock:
            event = self._events.get(event_id)
        if event is None:
            raise WebhookEventNotFoundError(event_id)
        if event.status == "delivered":
            return event

        handlers = self._handlers.get(event.event_type, [])
        for attempt in range(event.delivery_attempts + 1, self._max_attempts + 1):
            error_message: str | None = None
            try:
                for handler in handlers:
                    handler(event.payload)
            except Exception as error:  # noqa: BLE001 - handler failures are data
                error_message = f"{type(error).__name__}: {error}"
            event.deliveries.append(
                WebhookDelivery(
                    delivery_id=str(uuid4()),
                    event_id=event.event_id,
                    attempt_number=attempt,
                    status="failed" if error_message else "success",
                    response_code=500 if error_message else 200,
                    error=error_message,
                    attempted_at=_now(),
                )
            )
            event.delivery_attempts = attempt
            if error_message is None:
                event.status = "delivered"
                event.updated_at = _now()
                break
        if event.status != "delivered":
            event.status = "failed"
            event.updated_at = _now()

        with self._lock:
            self._events[event_id] = event
        return event

    def get(self, event_id: str) -> WebhookEvent:
        """Return an event by identifier."""
        with self._lock:
            event = self._events.get(event_id)
        if event is None:
            raise WebhookEventNotFoundError(event_id)
        return event

    def list(self, limit: int = 50) -> list[WebhookEvent]:
        """Return the most recent events."""
        with self._lock:
            events = list(self._events.values())
        return events[-limit:]

    @staticmethod
    def _validate_event(event_type: str) -> None:
        if event_type not in KNOWN_EVENTS:
            raise UnknownEventError(
                f"Unknown event type '{event_type}'. "
                f"Known events are: {', '.join(sorted(KNOWN_EVENTS))}."
            )


webhooks = WebhookProcessor()

__all__ = [
    "KNOWN_EVENTS",
    "InvalidSignatureError",
    "UnknownEventError",
    "WebhookDelivery",
    "WebhookEvent",
    "WebhookEventNotFoundError",
    "WebhookProcessor",
    "WebhookSecretError",
    "signature_for",
    "verify_signature",
    "webhooks",
]
