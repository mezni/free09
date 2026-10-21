"""Centralized error tracking for telco platform services."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel

logger = logging.getLogger("telco-platform-errors")


class ErrorInfo(BaseModel):
    """Structured error information for centralized tracking."""

    error_id: str
    timestamp: str
    service: str
    endpoint: str
    error_type: str
    message: str
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ErrorTracker:
    """Centralized error tracking and monitoring."""

    _error_buffer: List[ErrorInfo] = []
    _max_buffer_size: int = 1000

    @classmethod
    def track(
        cls,
        service: str,
        endpoint: str,
        error_type: str,
        message: str,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> ErrorInfo:
        """Track an error for centralized monitoring."""
        error_id = f"err-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
        error = ErrorInfo(
            error_id=error_id,
            timestamp=datetime.utcnow().isoformat(),
            service=service,
            endpoint=endpoint,
            error_type=error_type,
            message=message,
            request_id=request_id,
            details=details,
        )

        # Add to buffer (with size limit)
        cls._error_buffer.append(error)
        if len(cls._error_buffer) > cls._max_buffer_size:
            cls._error_buffer = cls._error_buffer[-cls._max_buffer_size :]

        # Log the error
        logger.error(
            json.dumps(
                {
                    "error_id": error_id,
                    "service": service,
                    "endpoint": endpoint,
                    "error_type": error_type,
                    "message": message,
                }
            )
        )

        return error

    @classmethod
    def get_recent_errors(cls, limit: int = 50) -> List[ErrorInfo]:
        """Get recent tracked errors."""
        return cls._error_buffer[-limit:]

    @classmethod
    def clear_errors(cls) -> None:
        """Clear the error buffer."""
        cls._error_buffer.clear()
