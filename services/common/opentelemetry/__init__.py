"""OpenTelemetry distributed tracing for telco platform services (FR-040).

The implementation lives in :mod:`src.observability.tracing`; this module keeps
the phase-5 import path stable.
"""

from src.observability.tracing import (
    DEFAULT_SERVICE_NAME,
    TracingConfig,
    TracingHandle,
    TracingMiddleware,
    configure_tracing,
    instrument_app,
)

__all__ = [
    "DEFAULT_SERVICE_NAME",
    "TracingConfig",
    "TracingHandle",
    "TracingMiddleware",
    "configure_tracing",
    "instrument_app",
]
