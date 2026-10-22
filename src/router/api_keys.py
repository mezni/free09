"""API key router (FR-043)."""

from fastapi import APIRouter, status

from src.api.endpoints.api_keys import (
    APIKeyCreateRequest,
    APIKeyUpdateRequest,
    create_api_key,
    delete_api_key,
    get_api_key,
    list_api_keys,
    update_api_key,
)
from src.services.api_keys import APIKeyCreated, APIKeyRead

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

router.add_api_route(
    "",
    create_api_key,
    methods=["POST"],
    response_model=APIKeyCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Create an API key",
)
router.add_api_route(
    "",
    list_api_keys,
    methods=["GET"],
    response_model=list[APIKeyRead],
    summary="List API keys",
)
router.add_api_route(
    "/{prefix}",
    get_api_key,
    methods=["GET"],
    response_model=APIKeyRead,
    summary="Get an API key",
)
router.add_api_route(
    "/{prefix}",
    update_api_key,
    methods=["PATCH"],
    response_model=APIKeyRead,
    summary="Update an API key",
)
router.add_api_route(
    "/{prefix}",
    delete_api_key,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke an API key",
)

__all__ = [
    "APIKeyCreateRequest",
    "APIKeyUpdateRequest",
    "router",
]
