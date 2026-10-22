"""Webhook validation and processing for the auth service (FR-044).

The implementation lives in :mod:`src.services.webhooks`; this module keeps the
phase-5 import path stable.
"""

from src.services.webhooks import (
    KNOWN_EVENTS,
    InvalidSignatureError,
    UnknownEventError,
    WebhookDelivery,
    WebhookEvent,
    WebhookEventNotFoundError,
    WebhookProcessor,
    WebhookSecretError,
    signature_for,
    verify_signature,
    webhooks,
)

WEBHOOK_PERSON_CREATED = "person.created"
WEBHOOK_PERSON_UPDATED = "person.updated"
WEBHOOK_PERSON_DELETED = "person.deleted"

__all__ = [
    "KNOWN_EVENTS",
    "WEBHOOK_PERSON_CREATED",
    "WEBHOOK_PERSON_DELETED",
    "WEBHOOK_PERSON_UPDATED",
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
