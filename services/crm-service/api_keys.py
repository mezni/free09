"""API key management UI (CRUD) for US2."""

from typing import List, Optional
from pydantic import BaseModel, EmailStr


class APIKeyCreate(BaseModel):
    """Schema for creating a new API key."""
    person_id: str
    scopes: Optional[List[str]] = None


class APIKeyResponse(BaseModel):
    """Schema for API key response."""
    id: str
    prefix: str
    scopes: List[str]
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None


class APIKeyCRUD:
    """API key CRUD operations."""

    @staticmethod
    def create_key(person_id: str, scopes: Optional[List[str]] = None) -> APIKeyResponse:
        """Create a new API key for a person."""
        # In production, this would generate a hash, prefix, etc.
        import uuid
        key_id = str(uuid.uuid4())
        prefix = uuid.uuid4().hex[:8]
        now = "2026-01-01T00:00:00Z"  # Would be datetime.utcnow().isoformat()
        
        return APIKeyResponse(
            id=key_id,
            prefix=prefix,
            scopes=scopes or [],
            is_active=True,
            created_at=now,
        )

    @staticmethod
    def get_key(key_id: str) -> Optional[APIKeyResponse]:
        """Retrieve an API key by ID."""
        # In production, this would query the database
        return None

    @staticmethod
    def update_key(key_id: str, is_active: bool = None, scopes: List[str] = None) -> Optional[APIKeyResponse]:
        """Update an API key (activate/deactivate or change scopes)."""
        # In production, this would update the database
        return None

    @staticmethod
    def delete_key(key_id: str) -> bool:
        """Delete/soft-delete an API key."""
        # In production, this would delete from the database
        return False
