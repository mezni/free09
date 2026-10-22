"""API key management (CRUD) for the CRM service (FR-043).

The implementation lives in :mod:`src.services.api_keys`; this module keeps the
phase-5 import path stable.
"""

from src.services.api_keys import (
    ALLOWED_SCOPES,
    APIKeyCreated,
    APIKeyInactiveError,
    APIKeyNotFoundError,
    APIKeyRead,
    APIKeyRecord,
    APIKeyScopeError,
    APIKeyStore,
    UnknownScopeError,
    api_keys,
)

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
