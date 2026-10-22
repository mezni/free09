"""Main FastAPI application entry point"""

import logging
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from src.database import create_all, engine
from src.middleware.logging import install_logging, log_buffer
from src.middleware.metrics import install_metrics
from src.observability.errors import (
    ErrorTrackingMiddleware,
    build_error_response,
)
from src.observability.tracing import TracingConfig, configure_tracing, instrument_app
from src.router.analytics import router as analytics_router
from src.router.api_keys import router as api_keys_router
from src.router.observability import router as observability_router
from src.router.webhooks import router as webhooks_router

logger = logging.getLogger(__name__)

SERVICE_NAME = "telco-platform"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Prepare the database schema before the application starts serving."""
    create_all()
    yield
    tracing = getattr(app.state, "tracing", None)
    if tracing is not None:
        tracing.shutdown()


# Create main app
app = FastAPI(
    title="Telco Platform API",
    version="0.1.0",
    description="Telco platform extension - build-phase8",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "analytics", "description": "Advanced analytics endpoints"},
        {
            "name": "ai-metrics",
            "description": "AI/ML model metrics and anomaly detection",
        },
        {"name": "admin", "description": "Admin UI and role-based access"},
        {"name": "partner", "description": "External partner integrations"},
        {"name": "compliance", "description": "Compliance and regulatory reporting"},
        {"name": "feature-flags", "description": "Feature flag framework"},
        {"name": "health", "description": "Liveness and readiness probes"},
        {"name": "api-keys", "description": "API key lifecycle management"},
        {"name": "webhooks", "description": "Webhook validation and delivery"},
        {
            "name": "observability",
            "description": "Logs, metrics, alerts and incident runbooks",
        },
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Structured request logs are written to a local buffer and never block the
# request path on Loki availability (FR-050).
app.state.log_buffer = log_buffer
install_logging(app, SERVICE_NAME, buffer=log_buffer)

# Distributed tracing (FR-040). Tracing is fail-open: an unreachable collector
# never fails a request.
tracing_handle = configure_tracing(TracingConfig.from_env(SERVICE_NAME))
app.state.tracing = tracing_handle
instrument_app(app, tracing_handle)

# Centralized error tracking (FR-041).
app.add_middleware(ErrorTrackingMiddleware, service_name=SERVICE_NAME)

# Base API router
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(analytics_router, tags=["analytics"])
api_router.include_router(api_keys_router)
api_router.include_router(webhooks_router)
api_router.include_router(observability_router)


def database_ready() -> bool:
    """Return whether the configured database answers a trivial query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.warning("Readiness probe could not reach the database", exc_info=True)
        return False


def _probe_payload() -> dict[str, object]:
    ready = database_ready()
    return {
        "status": "healthy" if ready else "unhealthy",
        "services": {
            "postgres": "healthy" if ready else "unhealthy",
            "redis": "not_configured",
        },
    }


@app.get("/healthz", tags=["health"])
async def liveness_probe() -> dict[str, str]:
    """Liveness probe: the process is alive and can answer HTTP."""
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz", tags=["health"])
async def readiness_probe() -> JSONResponse:
    """Readiness probe: the service can reach its dependencies."""
    payload = _probe_payload()
    code = status.HTTP_200_OK if payload["status"] == "healthy" else 503
    return JSONResponse(status_code=code, content=payload)


@app.get("/health", tags=["health"])
async def health_check() -> JSONResponse:
    """Readiness alias retained for the phase-5 health contract."""
    return await readiness_probe()


# Health check endpoint under the versioned API
@api_router.get("/health", tags=["health"])
async def versioned_health_check() -> JSONResponse:
    """Health check endpoint"""
    return await readiness_probe()


# Root endpoint
@api_router.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "message": "Telco Platform API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# Add middleware for request ID tracking
@app.middleware("http")
async def add_request_id(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    """Add request ID for tracing (Art. VIII - Observability)"""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, error: Exception
) -> JSONResponse:
    """Return the canonical error envelope for unhandled exceptions."""
    request_id = getattr(request.state, "request_id", None)
    payload = build_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="The service could not complete the request.",
        request_id=request_id,
        service=SERVICE_NAME,
    )
    return JSONResponse(status_code=500, content=payload)


# Include the API router in the app
app.include_router(api_router)

# Prometheus metrics endpoint and request instrumentation (FR-051).
install_metrics(app, SERVICE_NAME)
