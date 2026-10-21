"""Request/response logging middleware for observability."""

import json
import logging
from typing import Any, Dict, Optional
import time

logger = logging.getLogger("telco-platform")


class LoggingMiddleware:
    """Middleware to log request/response details for observability."""

    @staticmethod
    def log_request(
        method: str,
        path: str,
        query_string: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log incoming request details."""
        log_data: Dict[str, Any] = {
            "event": "request",
            "method": method,
            "path": path,
            "query_string": query_string,
            "timestamp": time.time(),
        }
        if body:
            log_data["request_body"] = body
        logger.info(json.dumps(log_data))

    @staticmethod
    def log_response(
        path: str,
        status_code: int,
        response_body: Optional[Any] = None,
        duration_ms: Optional[float] = None,
    ) -> None:
        """Log response details."""
        log_data: Dict[str, Any] = {
            "event": "response",
            "path": path,
            "status_code": status_code,
            "timestamp": time.time(),
        }
        if response_body is not None:
            # Sanitize sensitive data before logging
            sanitized = LoggingMiddleware._sanitize(log_data.get("response_body", {}))
            log_data["response_body"] = sanitized
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
        logger.info(json.dumps(log_data))

    @staticmethod
    def _sanitize(data: Any) -> Any:
        """Remove sensitive fields from data before logging."""
        if isinstance(data, dict):
            sensitive_keys = {"password", "token", "secret", "key_hash"}
            return {
                k: LoggingMiddleware._sanitize(v) if k not in sensitive_keys else "[Redacted]"
                for k, v in data.items()
            }
        if isinstance(data, list):
            return [LoggingMiddleware._sanitize(item) for item in data]
        return data
