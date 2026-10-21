"""OAuth2.1 authentication middleware."""

from typing import Optional

from fastapi import Depends, HTTPAuthorizationCredentials, HTTPException


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(),
) -> Optional[dict]:
    """Extract and validate OAuth2.1 bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header",
        )

    token = credentials.credentials

    # OAuth2.1 validation - in production, validate against auth server
    # For now, check token format (non-empty JWT-like string)
    if not token or "." not in token:
        raise HTTPException(
            status_code=401,
            detail="Invalid OAuth2.1 token format",
        )

    return {"sub": "user", "scopes": ["openid", "profile", "email"]}


def require_scopes(*required: str):
    """Create a dependency that checks for required OAuth2.1 scopes."""

    def dependency(user: dict = Depends(get_current_user)) -> dict:
        user_scopes: set[str] = set(user.get("scopes", []))
        for scope in required:
            if scope not in user_scopes:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing required scope: {scope}",
                )
        return user

    return dependency
