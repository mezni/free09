"""API key CRUD endpoints (FR-043)."""

from __future__ import annotations

from fastapi import HTTPException, Query, status
from pydantic import BaseModel, Field

from src.services.api_keys import (
    APIKeyCreated,
    APIKeyNotFoundError,
    APIKeyRead,
    APIKeyRecord,
    UnknownScopeError,
    api_keys,
)


class APIKeyCreateRequest(BaseModel):
    """Request body for creating an API key."""

    person_id: str = Field(min_length=1, max_length=100)
    scopes: list[str] = Field(default_factory=list)


class APIKeyUpdateRequest(BaseModel):
    """Request body for updating an API key."""

    is_active: bool | None = None
    scopes: list[str] | None = None


def _public(record: APIKeyRecord) -> APIKeyRead:
    return APIKeyRead(**record.model_dump(exclude={"key_hash"}))


def create_api_key(payload: APIKeyCreateRequest) -> APIKeyCreated:
    """Create a key; the plaintext secret is returned only in this response."""
    try:
        return api_keys.create(payload.person_id, payload.scopes)
    except UnknownScopeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error


def list_api_keys(
    person_id: str | None = Query(default=None, max_length=100),
    include_inactive: bool = Query(default=True),
) -> list[APIKeyRead]:
    """List API keys, optionally for one person."""
    return [
        _public(record)
        for record in api_keys.list_keys(person_id, include_inactive=include_inactive)
    ]


def get_api_key(prefix: str) -> APIKeyRead:
    """Return one API key."""
    try:
        return _public(api_keys.get(prefix))
    except APIKeyNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key '{prefix}' was not found",
        ) from error


def update_api_key(prefix: str, payload: APIKeyUpdateRequest) -> APIKeyRead:
    """Activate/deactivate a key or replace its scopes."""
    try:
        return _public(
            api_keys.update(prefix, is_active=payload.is_active, scopes=payload.scopes)
        )
    except APIKeyNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key '{prefix}' was not found",
        ) from error
    except UnknownScopeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error


def delete_api_key(prefix: str) -> None:
    """Revoke an API key."""
    if not api_keys.delete(prefix):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key '{prefix}' was not found",
        )


__all__ = [
    "APIKeyCreateRequest",
    "APIKeyUpdateRequest",
    "create_api_key",
    "delete_api_key",
    "get_api_key",
    "list_api_keys",
    "update_api_key",
]
