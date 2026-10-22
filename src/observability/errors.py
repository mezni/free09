"""Centralized error tracking (FR-041) and the canonical error envelope."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("telco-platform-errors")

SERVICE_NAME = "telco-platform"

ERROR_CODES = {
    "validation": "VALIDATION_ERROR",
    "authentication": "AUTHENTICATION_ERROR",
    "authorization": "AUTHORIZATION_ERROR",
    "not_found": "NOT_FOUND",
    "rate_limit": "RATE_LIMIT_EXCEEDED",
    "server_error": "INTERNAL_SERVER_ERROR",
}


class ErrorInfo(BaseModel):
    """Structured error information for centralized tracking."""

    error_id: str
    timestamp: str
    service: str
    endpoint: str
    error_type: str
    message: str
    request_id: str | None = None
    details: dict[str, Any] | None = None


class ErrorTracker:
    """In-process buffer and structured log sink for service errors."""

    _error_buffer: list[ErrorInfo] = []
    _max_buffer_size: int = 1000

    @classmethod
    def track(
        cls,
        service: str,
        endpoint: str,
        error_type: str,
        message: str,
        request_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> ErrorInfo:
        """Track an error, returning the record that was stored."""
        error_id = f"err-{datetime.now(timezone.utc):%Y%m%d%H%M%S}-{uuid4().hex[:8]}"
        error = ErrorInfo(
            error_id=error_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            service=service,
            endpoint=endpoint,
            error_type=error_type,
            message=message,
            request_id=request_id,
            details=details,
        )

        cls._error_buffer.append(error)
        if len(cls._error_buffer) > cls._max_buffer_size:
            cls._error_buffer = cls._error_buffer[-cls._max_buffer_size :]

        logger.error(
            json.dumps(
                {
                    "error_id": error_id,
                    "service": service,
                    "endpoint": endpoint,
                    "error_type": error_type,
                    "message": message,
                    "request_id": request_id,
                }
            )
        )
        return error

    @classmethod
    def get_recent_errors(cls, limit: int = 50) -> list[ErrorInfo]:
        """Return the most recently tracked errors."""
        return cls._error_buffer[-limit:]

    @classmethod
    def clear_errors(cls) -> None:
        """Clear the buffer (used by tests)."""
        cls._error_buffer.clear()


def _service_name() -> str:
    """Return the configured service name, falling back to the platform name."""
    return os.environ.get("TELECO_SERVICE_NAME", "").strip() or SERVICE_NAME


def build_error_response(
    *,
    code: str,
    message: str,
    request_id: str | None,
    service: str | None = None,
    error_id: str | None = None,
) -> dict[str, Any]:
    """Build the canonical error envelope from the phase-5 API contract."""
    return {
        "error_id": error_id
        or f"err-{datetime.now(timezone.utc):%Y%m%d%H%M%S}-{uuid4().hex[:8]}",
        "code": code,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "service": service or _service_name(),
    }


class ErrorTrackingMiddleware:
    """Record unhandled exceptions with request, service, and error type."""

    def __init__(self, app: ASGIApp, service_name: str | None = None) -> None:
        self.app = app
        self.service_name = service_name or _service_name()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = self._request_id(scope)

        async def send_with_error_capture(message: Message) -> None:
            await send(message)

        try:
            await self.app(scope, receive, send_with_error_capture)
        except Exception as error:
            ErrorTracker.track(
                service=self.service_name,
                endpoint=str(scope.get("path", "/")),
                error_type=type(error).__name__,
                message=str(error),
                request_id=request_id,
            )
            raise

    @staticmethod
    def _request_id(scope: Scope) -> str | None:
        state = scope.get("state")
        if isinstance(state, dict):
            value = state.get("request_id")
            if isinstance(value, str):
                return value
        return None
