"""Webhook validation, idempotency and delivery tests (FR-044, TM116–TM118)."""

from __future__ import annotations

import pytest

from src.services.webhooks import (
    InvalidSignatureError,
    UnknownEventError,
    WebhookProcessor,
    WebhookSecretError,
    signature_for,
    verify_signature,
)

pytestmark = [pytest.mark.unit, pytest.mark.webhook]

SECRET = "test-webhook-secret"
PAYLOAD = {"event_type": "person.created", "id": "person-1"}


@pytest.fixture
def processor() -> WebhookProcessor:
    return WebhookProcessor(secret_provider=lambda: SECRET, max_attempts=3)


def _sign(payload: dict) -> str:
    import json

    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return signature_for(body, SECRET)


def test_signature_round_trip():
    """The exported helpers agree on a valid signature."""
    body = b'{"event_type":"person.created"}'
    signature = signature_for(body, SECRET)
    assert verify_signature(body, signature, SECRET) is True
    assert verify_signature(body, signature, "other") is False
    assert verify_signature(body, None, SECRET) is False


def test_subscribe_and_unsubscribe(processor: WebhookProcessor):
    """Subscriptions accept known events and reject unknown ones."""
    assert processor.subscribe(["person.created"]) == {"person.created"}
    assert processor.subscriptions() == {"person.created"}
    assert processor.unsubscribe(["person.created"]) == set()

    with pytest.raises(UnknownEventError):
        processor.subscribe(["person.exploded"])


def test_valid_event_is_delivered(processor: WebhookProcessor):
    """A correctly signed event reaches its handler."""
    received: list[dict] = []
    processor.register("person.created")(received.append)

    event, duplicate = processor.process(
        event_type="person.created",
        payload=PAYLOAD,
        signature=_sign(PAYLOAD),
    )

    assert duplicate is False
    assert event.status == "delivered"
    assert event.delivery_attempts == 1
    assert received == [PAYLOAD]


def test_invalid_signature_is_rejected_before_the_handler(
    processor: WebhookProcessor,
):
    """An invalid signature never reaches a handler and is not retried."""
    calls: list[dict] = []
    processor.register("person.created")(calls.append)

    with pytest.raises(InvalidSignatureError):
        processor.process(
            event_type="person.created",
            payload=PAYLOAD,
            signature="sha256=deadbeef",
        )

    assert calls == []
    assert processor.list() == []


def test_missing_secret_fails_closed():
    """With no configured secret, validation cannot succeed."""
    processor = WebhookProcessor(secret_provider=lambda: None)
    with pytest.raises(WebhookSecretError):
        processor.process(
            event_type="person.created",
            payload=PAYLOAD,
            signature=_sign(PAYLOAD),
        )


def test_unknown_event_is_rejected(processor: WebhookProcessor):
    """An event type outside the contract is rejected."""
    with pytest.raises(UnknownEventError):
        processor.process(
            event_type="person.exploded",
            payload={"event_type": "person.exploded"},
            signature=_sign({"event_type": "person.exploded"}),
        )


def test_idempotency_key_suppresses_a_duplicate(processor: WebhookProcessor):
    """A repeated idempotency key is acknowledged but not reprocessed."""
    calls: list[dict] = []
    processor.register("person.created")(calls.append)

    first, first_duplicate = processor.process(
        event_type="person.created",
        payload=PAYLOAD,
        signature=_sign(PAYLOAD),
        idempotency_key="event-1",
    )
    second, second_duplicate = processor.process(
        event_type="person.created",
        payload=PAYLOAD,
        signature=_sign(PAYLOAD),
        idempotency_key="event-1",
    )

    assert first_duplicate is False
    assert second_duplicate is True
    assert first.event_id == second.event_id
    assert len(calls) == 1


def test_failed_handler_is_retried_until_success(processor: WebhookProcessor):
    """Delivery is at-least-once: retries continue until a handler succeeds."""
    attempts: list[int] = []

    def flaky_handler(payload: dict) -> None:
        attempts.append(len(attempts) + 1)
        if len(attempts) < 3:
            raise RuntimeError("temporary failure")

    processor.register("person.created")(flaky_handler)

    event, duplicate = processor.process(
        event_type="person.created",
        payload=PAYLOAD,
        signature=_sign(PAYLOAD),
    )

    assert duplicate is False
    assert event.status == "delivered"
    assert event.delivery_attempts == 3
    assert len(attempts) == 3
    assert [delivery.status for delivery in event.deliveries] == [
        "failed",
        "failed",
        "success",
    ]


def test_exhausted_retries_leave_a_failed_event(processor: WebhookProcessor):
    """A handler that never succeeds exhausts the attempt budget."""
    processor.register("person.created")(
        lambda payload: (_ for _ in ()).throw(RuntimeError("permanent failure"))
    )

    event, _ = processor.process(
        event_type="person.created",
        payload=PAYLOAD,
        signature=_sign(PAYLOAD),
    )

    assert event.status == "failed"
    assert event.delivery_attempts == 3
    assert all(delivery.status == "failed" for delivery in event.deliveries)


def test_retry_resumes_a_failed_event(processor: WebhookProcessor):
    """A later retry can still deliver a previously failed event."""
    state = {"fail": True}

    def handler(payload: dict) -> None:
        if state["fail"]:
            raise RuntimeError("still down")

    processor.register("person.created")(handler)
    event, _ = processor.process(
        event_type="person.created",
        payload=PAYLOAD,
        signature=_sign(PAYLOAD),
    )
    assert event.status == "failed"

    state["fail"] = False
    processor._max_attempts = 4
    retried = processor.retry(event.event_id)
    assert retried.status == "delivered"
