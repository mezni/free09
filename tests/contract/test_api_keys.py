"""API key lifecycle and scope-validation tests (FR-043, TM113–TM115)."""

from __future__ import annotations

import pytest

from src.services.api_keys import (
    ALLOWED_SCOPES,
    APIKeyInactiveError,
    APIKeyNotFoundError,
    APIKeyScopeError,
    APIKeyStore,
    UnknownScopeError,
)

pytestmark = [pytest.mark.unit, pytest.mark.key]


@pytest.fixture
def store() -> APIKeyStore:
    return APIKeyStore()


def test_create_returns_the_secret_exactly_once(store: APIKeyStore):
    """Creation returns the plaintext key, and the store keeps only a hash."""
    created = store.create("person-1", ["read", "write"])
    assert created.key.startswith(f"{created.prefix}.")
    assert created.scopes == ["read", "write"]
    assert created.is_active is True

    stored = store.get(created.prefix)
    assert stored.key_hash
    assert created.key.split(".", 1)[1] not in stored.key_hash


def test_get_list_update_and_revoke(store: APIKeyStore):
    """The full CRUD lifecycle works and revocation is visible."""
    first = store.create("person-1", ["read"])
    second = store.create("person-2", ["write"])

    person_one = store.list_keys(person_id="person-1")
    assert [key.prefix for key in person_one] == [first.prefix]
    assert len(store.list_keys()) == 2

    updated = store.update(first.prefix, scopes=["read", "admin"])
    assert updated.scopes == ["read", "admin"]

    deactivated = store.update(second.prefix, is_active=False)
    assert deactivated.is_active is False
    active = store.list_keys(include_inactive=False)
    assert [key.prefix for key in active] == [first.prefix]

    assert store.delete(first.prefix) is True
    assert store.get(first.prefix).is_active is False
    assert store.delete("tf_missing") is False


def test_missing_key_raises(store: APIKeyStore):
    """Reading an unknown prefix reports not-found."""
    with pytest.raises(APIKeyNotFoundError):
        store.get("tf_missing")


def test_unknown_scopes_are_rejected_and_audited(store: APIKeyStore):
    """A scope the platform does not define is never granted."""
    with pytest.raises(UnknownScopeError):
        store.create("person-1", ["read", "superuser"])

    audits = store.audit_events()
    assert any(event["action"] == "api_key.scope_rejected" for event in audits)
    assert "superuser" in str(audits)


def test_update_rejects_unknown_scopes(store: APIKeyStore):
    """Scope validation also applies to updates."""
    created = store.create("person-1", ["read"])
    with pytest.raises(UnknownScopeError):
        store.update(created.prefix, scopes=["everything"])


def test_authenticate_accepts_a_valid_key_and_scope(store: APIKeyStore):
    """A valid key with the required scope authenticates."""
    created = store.create("person-1", ["read"])
    record = store.authenticate(created.key, "read")
    assert record.prefix == created.prefix


def test_authenticate_rejects_wrong_secret_scope_and_inactive_key(
    store: APIKeyStore,
):
    """Bad secrets, missing scopes and revoked keys are refused."""
    created = store.create("person-1", ["read"])

    with pytest.raises(APIKeyNotFoundError):
        store.authenticate(f"{created.prefix}.wrong-secret", "read")

    with pytest.raises(APIKeyScopeError):
        store.authenticate(created.key, "admin")

    store.delete(created.prefix)
    with pytest.raises(APIKeyInactiveError):
        store.authenticate(created.key, "read")


def test_known_scopes_are_the_documented_set():
    """The allowed scopes match the API contract."""
    assert {"read", "write", "admin"} == ALLOWED_SCOPES
