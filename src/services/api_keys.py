"""API key lifecycle management with scope-based access control (FR-043).

Keys are held in memory for this phase: the phase-5 specification explicitly
places database-schema changes out of scope, so the store is process-local but
implements the full create/read/update/delete lifecycle and scope validation.
Only a hash of the key secret is retained.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import threading
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

ALLOWED_SCOPES: frozenset[str] = frozenset({"read", "write", "admin"})
"""The scopes the platform defines. An unknown scope is a rejection, not a grant."""

KEY_PREFIX = "tf"


class UnknownScopeError(ValueError):
    """Raised when a caller asks for a scope the platform does not define."""


class APIKeyNotFoundError(KeyError):
    """Raised when no key matches the supplied identifier."""


class APIKeyInactiveError(PermissionError):
    """Raised when a matching key is revoked."""


class APIKeyScopeError(PermissionError):
    """Raised when a valid key lacks the scope a caller requires."""


class APIKeyRecord(BaseModel):
    """The stored representation of an API key."""

    id: str
    person_id: str
    prefix: str
    scopes: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: str
    updated_at: str | None = None
    key_hash: str = Field(exclude=True)


class APIKeyRead(BaseModel):
    """The public representation of an API key (never includes the secret)."""

    id: str
    person_id: str
    prefix: str
    scopes: list[str]
    is_active: bool
    created_at: str
    updated_at: str | None = None


class APIKeyCreated(APIKeyRead):
    """The one-time response returned when a key is created."""

    key: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_scopes(scopes: list[str] | None) -> list[str]:
    requested = list(dict.fromkeys(scopes or []))
    unknown = sorted(set(requested) - ALLOWED_SCOPES)
    if unknown:
        raise UnknownScopeError(
            f"Unknown scope(s): {', '.join(unknown)}. "
            f"Allowed scopes are: {', '.join(sorted(ALLOWED_SCOPES))}."
        )
    return requested


def _hash_secret(secret: str, pepper: str = "") -> str:
    return hashlib.sha256(f"{pepper}{secret}".encode("utf-8")).hexdigest()


class APIKeyStore:
    """Thread-safe in-memory API key store."""

    def __init__(self, pepper: str = "") -> None:
        self._records: dict[str, APIKeyRecord] = {}
        self._lock = threading.RLock()
        self._pepper = pepper
        self._audit: list[dict[str, Any]] = []

    def reset(self) -> None:
        """Remove every key and audit entry (used by tests)."""
        with self._lock:
            self._records.clear()
            self._audit.clear()

    def audit_events(self) -> list[dict[str, Any]]:
        """Return a copy of the security-relevant decisions made by the store."""
        with self._lock:
            return [dict(event) for event in self._audit]

    def _record_audit(self, action: str, **details: Any) -> None:
        self._audit.append({"action": action, "at": _now(), **details})

    def create(self, person_id: str, scopes: list[str] | None = None) -> APIKeyCreated:
        """Create a key and return the plaintext secret exactly once."""
        try:
            validated = _validate_scopes(scopes)
        except UnknownScopeError as error:
            self._record_audit(
                "api_key.scope_rejected",
                person_id=person_id,
                requested_scopes=list(scopes or []),
                reason=str(error),
            )
            raise

        key_id = str(uuid4())
        prefix = f"{KEY_PREFIX}_{secrets.token_hex(4)}"
        secret = secrets.token_urlsafe(32)
        record = APIKeyRecord(
            id=key_id,
            person_id=person_id,
            prefix=prefix,
            scopes=validated,
            is_active=True,
            created_at=_now(),
            key_hash=_hash_secret(secret, self._pepper),
        )
        with self._lock:
            self._records[prefix] = record
        self._record_audit("api_key.created", person_id=person_id, prefix=prefix)
        return APIKeyCreated(
            **record.model_dump(exclude={"key_hash"}),
            key=f"{prefix}.{secret}",
        )

    def get(self, prefix: str) -> APIKeyRecord:
        """Return a key by prefix, raising when it does not exist."""
        with self._lock:
            record = self._records.get(prefix)
        if record is None:
            raise APIKeyNotFoundError(prefix)
        return record

    def list_keys(
        self, person_id: str | None = None, *, include_inactive: bool = True
    ) -> list[APIKeyRecord]:
        """Return keys, optionally scoped to one person."""
        with self._lock:
            records = list(self._records.values())
        if person_id is not None:
            records = [record for record in records if record.person_id == person_id]
        if not include_inactive:
            records = [record for record in records if record.is_active]
        return sorted(records, key=lambda record: record.created_at)

    def update(
        self,
        prefix: str,
        *,
        is_active: bool | None = None,
        scopes: list[str] | None = None,
    ) -> APIKeyRecord:
        """Activate/deactivate a key or replace its scopes."""
        validated = _validate_scopes(scopes) if scopes is not None else None
        with self._lock:
            record = self._records.get(prefix)
            if record is None:
                raise APIKeyNotFoundError(prefix)
            changes: dict[str, Any] = {"updated_at": _now()}
            if is_active is not None:
                changes["is_active"] = is_active
            if validated is not None:
                changes["scopes"] = validated
            updated = record.model_copy(update=changes)
            self._records[prefix] = updated
        self._record_audit("api_key.updated", prefix=prefix)
        return updated

    def delete(self, prefix: str) -> bool:
        """Revoke a key. Returns True when a key was revoked."""
        with self._lock:
            record = self._records.get(prefix)
            if record is None:
                return False
            self._records[prefix] = record.model_copy(
                update={"is_active": False, "updated_at": _now()}
            )
        self._record_audit("api_key.revoked", prefix=prefix)
        return True

    def authenticate(
        self, raw_key: str, required_scope: str | None = None
    ) -> APIKeyRecord:
        """Validate a presented key and, optionally, one required scope."""
        prefix, _, secret = raw_key.partition(".")
        if not prefix or not secret:
            self._record_audit("api_key.rejected", reason="malformed key")
            raise APIKeyNotFoundError(raw_key)

        with self._lock:
            record = self._records.get(prefix)

        if record is None:
            self._record_audit("api_key.rejected", prefix=prefix, reason="unknown key")
            raise APIKeyNotFoundError(prefix)
        if not record.is_active:
            self._record_audit("api_key.rejected", prefix=prefix, reason="inactive key")
            raise APIKeyInactiveError(prefix)
        if not hmac.compare_digest(record.key_hash, _hash_secret(secret, self._pepper)):
            self._record_audit("api_key.rejected", prefix=prefix, reason="bad secret")
            raise APIKeyNotFoundError(prefix)
        if required_scope is not None and required_scope not in record.scopes:
            self._record_audit(
                "api_key.rejected",
                prefix=prefix,
                reason="missing scope",
                required_scope=required_scope,
            )
            raise APIKeyScopeError(required_scope)
        return record


api_keys = APIKeyStore()

__all__ = [
    "ALLOWED_SCOPES",
    "APIKeyCreated",
    "APIKeyInactiveError",
    "APIKeyNotFoundError",
    "APIKeyRead",
    "APIKeyRecord",
    "APIKeyScopeError",
    "APIKeyStore",
    "UnknownScopeError",
    "api_keys",
]
