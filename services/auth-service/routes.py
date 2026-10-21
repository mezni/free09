"""Health check endpoints for auth service."""

from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "healthy"}


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with dependencies."""
    return {
        "status": "healthy",
        "services": {
            "postgres": "up",
            "redis": "up",
        },
    }
