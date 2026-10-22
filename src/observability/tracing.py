"""OpenTelemetry tracing configuration and ASGI middleware (FR-040).

Tracing is deliberately fail-open for the request path: a collector that is
unreachable, an exporter that raises, or a misconfigured endpoint must never
turn a healthy request into a failed one. The middleware records what it can
and continues serving.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass

from opentelemetry import context as otel_context
from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
)
from opentelemetry.trace import SpanKind, Status, StatusCode
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("telco-platform-tracing")

DEFAULT_SERVICE_NAME = "telco-platform"
"""Name used when neither configuration nor the environment names a service."""

_OTEL_ENDPOINTS = (
    "TELECO_OTEL_EXPORTER_OTLP_ENDPOINT",
    "OTEL_EXPORTER_OTLP_ENDPOINT",
)


@dataclass(frozen=True)
class TracingConfig:
    """Resolved tracing configuration."""

    service_name: str
    endpoint: str | None = None
    enabled: bool = True

    @classmethod
    def from_env(cls, service_name: str | None = None) -> TracingConfig:
        """Build the configuration from the documented environment variables."""
        endpoint = ""
        for variable in _OTEL_ENDPOINTS:
            value = os.environ.get(variable, "").strip()
            if value:
                endpoint = value
                break

        return cls(
            service_name=(
                service_name
                or os.environ.get("TELECO_SERVICE_NAME", "").strip()
                or DEFAULT_SERVICE_NAME
            ),
            endpoint=endpoint or None,
        )


@dataclass
class TracingHandle:
    """The provider, tracer and settings created by :func:`configure_tracing`."""

    config: TracingConfig
    provider: TracerProvider
    tracer: trace.Tracer

    def shutdown(self) -> None:
        """Flush and stop the span processors."""
        try:
            self.provider.shutdown()
        except Exception:  # pragma: no cover - defensive shutdown
            logger.exception("Failed to shut down the tracing provider")


def _build_exporter(endpoint: str) -> SpanExporter | None:
    """Create the OTLP/HTTP exporter, or return None when it cannot be built."""
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        return OTLPSpanExporter(endpoint=endpoint)
    except Exception:
        logger.exception("OpenTelemetry exporter could not be configured")
        return None


def configure_tracing(
    config: TracingConfig | None = None,
    *,
    exporter: SpanExporter | None = None,
    set_global: bool = True,
) -> TracingHandle | None:
    """Create a tracer provider for one service.

    Args:
        config: Resolved settings. When omitted the environment is read.
        exporter: Explicit exporter, primarily for tests. When supplied the
            spans are exported synchronously so assertions see them immediately.
        set_global: Register the provider globally. Tests normally pass
            ``False`` so that one process can create several providers.

    Returns:
        A handle, or ``None`` when tracing is disabled.
    """
    resolved = config or TracingConfig.from_env()
    if not resolved.enabled:
        return None

    resource = Resource.create(
        {
            "service.name": resolved.service_name,
            "service.version": "0.1.0",
            "deployment.environment": os.environ.get("TELECO_ENV", "dev"),
        }
    )
    provider = TracerProvider(resource=resource)

    chosen = exporter
    if chosen is None and resolved.endpoint:
        chosen = _build_exporter(resolved.endpoint)

    if chosen is not None:
        processor = (
            SimpleSpanProcessor(chosen)
            if exporter is not None
            else BatchSpanProcessor(chosen)
        )
        provider.add_span_processor(processor)

    if set_global:
        try:
            trace.set_tracer_provider(provider)
        except Exception:  # pragma: no cover - one provider per process
            logger.warning("A global tracer provider is already registered")

    return TracingHandle(
        config=resolved,
        provider=provider,
        tracer=provider.get_tracer("telco_platform"),
    )


def _header_map(scope: Scope) -> dict[str, str]:
    """Return the request headers as text, lower-cased."""
    headers: dict[str, str] = {}
    for raw_key, raw_value in scope.get("headers", []):
        try:
            key = raw_key.decode("latin-1").lower()
            headers[key] = raw_value.decode("latin-1")
        except (UnicodeDecodeError, AttributeError):  # pragma: no cover
            continue
    return headers


class TracingMiddleware:
    """Trace every HTTP request, propagating W3C trace context."""

    def __init__(self, app: ASGIApp, tracer: trace.Tracer, service_name: str) -> None:
        self.app = app
        self.tracer = tracer
        self.service_name = service_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        state = scope.setdefault("state", {})
        if isinstance(state, dict):
            state["tracing_service_name"] = self.service_name

        headers = _header_map(scope)
        parent = extract(headers)
        method = str(scope.get("method", "GET"))
        path = str(scope.get("path", "/"))
        status_code = 500

        try:
            span = self.tracer.start_span(
                name=f"{method} {path}",
                context=parent,
                kind=SpanKind.SERVER,
                attributes={
                    "service.name": self.service_name,
                    "http.request.method": method,
                    "url.path": path,
                    "url.scheme": str(scope.get("scheme", "http")),
                },
            )
        except Exception:  # pragma: no cover - tracing must not break requests
            logger.exception("Could not start a trace span; serving without tracing")
            await self.app(scope, receive, send)
            return

        token = otel_context.attach(trace.set_span_in_context(span))

        async def send_with_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.set_attribute("error.type", type(error).__name__)
            raise
        finally:
            span.set_attribute("http.response.status_code", status_code)
            otel_context.detach(token)
            try:
                span.end()
            except Exception:  # pragma: no cover - exporter failure is non-fatal
                logger.exception("Could not export a trace span")


def instrument_app(app: object, handle: TracingHandle | None) -> None:
    """Attach :class:`TracingMiddleware` to a Starlette/FastAPI application."""
    if handle is None:
        return

    add_middleware: Callable[..., Awaitable[None]] | None = getattr(
        app, "add_middleware", None
    )
    if add_middleware is None:  # pragma: no cover - defensive
        return

    add_middleware(
        TracingMiddleware,
        tracer=handle.tracer,
        service_name=handle.config.service_name,
    )


def trace_context_from_headers(headers: Mapping[str, str]) -> object:
    """Extract the upstream trace context from a mapping of headers."""
    return extract(dict(headers))
