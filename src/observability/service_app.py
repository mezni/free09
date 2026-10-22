"""Factory for the four domain service applications (FR-040, FR-042)."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from src.observability.errors import ErrorTrackingMiddleware, build_error_response
from src.observability.tracing import TracingConfig, configure_tracing, instrument_app


def _request_id_middleware(app: FastAPI) -> None:
    """Register middleware that stores and echoes a request identifier."""

    @app.middleware("http")
    async def add_request_id(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def create_service_app(
    service_name: str,
    *,
    readiness: Callable[[], bool] | None = None,
) -> FastAPI:
    """Create a FastAPI application with tracing, errors and health probes."""
    app = FastAPI(title=service_name, version="0.1.0")

    app.add_middleware(ErrorTrackingMiddleware, service_name=service_name)
    _request_id_middleware(app)

    handle = configure_tracing(TracingConfig.from_env(service_name), set_global=False)
    app.state.tracing = handle
    instrument_app(app, handle)

    @app.get("/healthz", tags=["health"])
    async def liveness() -> dict[str, str]:
        """Liveness probe: the process is running."""
        return {"status": "healthy", "service": service_name}

    @app.get("/readyz", tags=["health"])
    async def readiness_probe() -> JSONResponse:
        """Readiness probe: the service can serve requests."""
        ready = True if readiness is None else bool(readiness())
        payload = {
            "status": "healthy" if ready else "unhealthy",
            "services": {service_name: "healthy" if ready else "unhealthy"},
        }
        return JSONResponse(status_code=200 if ready else 503, content=payload)

    @app.get("/health", tags=["health"])
    async def detailed_health() -> JSONResponse:
        """Readiness alias retained for the phase-5 health contract."""
        return await readiness_probe()

    @app.exception_handler(Exception)
    async def unhandled_exception(request: Request, error: Exception) -> JSONResponse:
        """Return the canonical error envelope instead of a bare 500."""
        request_id = getattr(request.state, "request_id", None)
        payload = build_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="The service could not complete the request.",
            request_id=request_id,
            service=service_name,
        )
        return JSONResponse(status_code=500, content=payload)

    return app
