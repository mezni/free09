"""Main FastAPI application entry point"""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.database import create_all
from src.router.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare the database schema before the application starts serving."""
    create_all()
    yield


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

# Base API router
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(analytics_router, tags=["analytics"])


# Health check endpoint
@api_router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "telco-platform"}


# Root endpoint
@api_router.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Telco Platform API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# Add middleware for request logging
@app.middleware("http")
async def add_middleware_logging(request: Request, call_next):
    """Log incoming requests for observability (Art. VIII)"""
    response = await call_next(request)
    return response


# Add middleware for request ID tracking
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID for tracing (Art. VIII - Observability)"""
    import uuid

    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Include the API router in the app
app.include_router(api_router)
