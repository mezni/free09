"""Authentication service for telco platform."""

from src.observability.service_app import create_service_app

__version__ = "0.1.0"

app = create_service_app("auth-service")

__all__ = ["__version__", "app", "create_service_app"]
