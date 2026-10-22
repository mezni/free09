"""Authentication and authorization framework using OAuth2.0 (NFR-052)"""

from collections.abc import Awaitable, Callable
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordBearer,
)
from pydantic import BaseModel, Field

# OAuth2 password bearer for API key less auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Opaque bearer token scheme for scope-gated endpoints
bearer_scheme = HTTPBearer(auto_error=False)

# OAuth2 authorization code bearer for interactive auth
# Uses authorization_code flow - redirect to auth server, then exchange code for token
oauth2_authorization_code = OAuth2AuthorizationCodeBearer(
    tokenUrl="https://auth-service/token",
    authorizationUrl="https://auth-service/authorize",
    scopes={
        "read": "Read access",
        "write": "Write access",
        "admin": "Admin access",
    },
)


# Token data model
class TokenData(BaseModel):
    """Decoded token data"""

    scopes: Optional[list[str]] = Field(default=[], description="OAuth2 scopes")
    sub: Optional[str] = Field(default=None, description="Subject (user ID)")
    email: Optional[str] = Field(default=None, description="User email")


# Permission check utilities
def check_scope(token_scopes: list[str], required_scopes: list[str]) -> bool:
    """Check if token has required OAuth2 scopes"""
    if not required_scopes:
        return True
    token_set = set(token_scopes or [])
    required_set = set(required_scopes)
    return required_set.issubset(token_set)


def require_scopes(
    required_scopes: list[str],
) -> Callable[..., Awaitable[str]]:
    """FastAPI dependency to require specific OAuth2 scopes"""

    async def dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    ) -> str:
        # In production, decode and validate the JWT token here
        # For now, simulate scope validation
        token = credentials.credentials if credentials else ""
        token_scopes: list[str] = []  # Would be decoded from JWT
        if not check_scope(token_scopes, required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient scopes",
            )
        return token

    return dependency


# Role-based access control
class UserRole:
    """User roles for RBAC (Art. II - Domain Ownership)"""

    READ_ONLY = "read-only"
    WRITER = "writer"
    ADMIN = "admin"


ROLE_PERMISSIONS: dict[str, list[str]] = {
    UserRole.READ_ONLY: ["read"],
    UserRole.WRITER: ["read", "write"],
    UserRole.ADMIN: ["read", "write", "admin"],
}


def has_permission(role: str, required: list[str]) -> bool:
    """Check if a role has the required permissions"""
    permissions = ROLE_PERMISSIONS.get(role, [])
    return all(p in permissions for p in required)
