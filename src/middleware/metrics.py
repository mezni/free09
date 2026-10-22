"""Prometheus instrumentation for telco services (FR-051, TM128–TM130)."""

from __future__ import annotations

from time import perf_counter

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUESTS_TOTAL = Counter(
    "service_requests_total",
    "Total HTTP requests handled by a service.",
    ("service", "method", "endpoint", "status"),
)
REQUEST_DURATION = Histogram(
    "service_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("service", "method", "endpoint"),
)
ERRORS_TOTAL = Counter(
    "service_errors_total",
    "HTTP responses with a 5xx status.",
    ("service", "method", "endpoint", "status"),
)
SPANS_CREATED_TOTAL = Counter(
    "otel_spans_created_total",
    "Spans created by the local tracer.",
    ("service",),
)
SPANS_EXPORTED_SUCCESSFUL_TOTAL = Counter(
    "otel_spans_exported_successful_total",
    "Spans successfully exported.",
    ("service",),
)
MESH_FALLBACK_TOTAL = Counter(
    "service_mesh_fallback_total",
    "Requests that bypassed the service mesh and used the direct path.",
    ("service", "reason"),
)


def record_span_created(service: str = "telco-platform") -> None:
    """Record that the local tracer created a span."""
    SPANS_CREATED_TOTAL.labels(service=service).inc()


def record_span_exported(service: str = "telco-platform") -> None:
    """Record that a span was exported successfully."""
    SPANS_EXPORTED_SUCCESSFUL_TOTAL.labels(service=service).inc()


def record_mesh_fallback(service: str, reason: str = "sidecar_unavailable") -> None:
    """Record that a request used the direct path instead of the sidecar."""
    MESH_FALLBACK_TOTAL.labels(service=service, reason=reason).inc()


def metrics_payload() -> bytes:
    """Render the current registry in OpenMetrics-compatible text form."""
    return generate_latest()


async def metrics_endpoint(_: Request) -> Response:
    """Expose the Prometheus scrape endpoint."""
    return Response(content=metrics_payload(), media_type=CONTENT_TYPE_LATEST)


def _route_path(scope: Scope) -> str:
    route = scope.get("route")
    return str(getattr(route, "path", None) or scope.get("path", "/"))


class MetricsMiddleware:
    """Record request totals, durations and errors."""

    def __init__(self, app: ASGIApp, service_name: str) -> None:
        self.app = app
        self.service_name = service_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = str(scope.get("method", "GET"))
        endpoint = _route_path(scope)
        started = perf_counter()
        status_code = 500

        async def send_with_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        except Exception:
            status_code = 500
            raise
        finally:
            endpoint = _route_path(scope)
            duration = perf_counter() - started
            REQUESTS_TOTAL.labels(
                service=self.service_name,
                method=method,
                endpoint=endpoint,
                status=str(status_code),
            ).inc()
            REQUEST_DURATION.labels(
                service=self.service_name,
                method=method,
                endpoint=endpoint,
            ).observe(duration)
            if status_code >= 500:
                ERRORS_TOTAL.labels(
                    service=self.service_name,
                    method=method,
                    endpoint=endpoint,
                    status=str(status_code),
                ).inc()


def install_metrics(app: object, service_name: str) -> None:
    """Attach the metrics middleware and register ``GET /metrics``."""
    add_middleware = getattr(app, "add_middleware", None)
    add_api_route = getattr(app, "add_api_route", None)
    if add_middleware is not None:
        add_middleware(MetricsMiddleware, service_name=service_name)
    if add_api_route is not None:
        add_api_route(
            "/metrics",
            metrics_endpoint,
            methods=["GET"],
            include_in_schema=False,
        )


__all__ = [
    "ERRORS_TOTAL",
    "MESH_FALLBACK_TOTAL",
    "MetricsMiddleware",
    "REQUEST_DURATION",
    "REQUESTS_TOTAL",
    "SPANS_CREATED_TOTAL",
    "SPANS_EXPORTED_SUCCESSFUL_TOTAL",
    "install_metrics",
    "metrics_endpoint",
    "metrics_payload",
    "record_mesh_fallback",
    "record_span_created",
    "record_span_exported",
]
