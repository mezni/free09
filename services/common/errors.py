"""Centralized error tracking for telco platform services (FR-041).

The implementation lives in :mod:`src.observability.errors` so that the shared
application package owns it; this module keeps the phase-5 import path stable.
"""

from src.observability.errors import (
    ERROR_CODES,
    ErrorInfo,
    ErrorTracker,
    build_error_response,
)

__all__ = ["ERROR_CODES", "ErrorInfo", "ErrorTracker", "build_error_response"]
