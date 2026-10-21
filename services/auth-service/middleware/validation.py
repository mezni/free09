"""Request validation middleware using Pydantic v2."""

from typing import Any, Optional

from fastapi import HTTPException, Request
from pydantic import BaseModel, validator


class PersonCreate(BaseModel):
    """Pydantic model for person creation request validation."""

    name: str
    email: str
    phone: Optional[str] = None

    @validator("email")
    def validate_email_format(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @validator("phone")
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone format (E.164)."""
        if v is not None and not v.startswith("+"):
            raise ValueError("Phone must be in E.164 format (e.g., +1234567890)")
        return v


class PersonUpdate(BaseModel):
    """Pydantic model for person update request validation."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    @validator("email")
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format."""
        if v is not None and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @validator("phone")
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone format."""
        if v is not None and not v.startswith("+"):
            raise ValueError("Phone must be in E.164 format")
        return v


async def validate_request(request: Request, model: type[BaseModel]) -> Any:
    """Validate request body against Pydantic model."""
    try:
        body = await request.json()
        validated = model(**body)
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
