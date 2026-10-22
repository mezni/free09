"""Database dependency for FastAPI application"""

import os
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.models import Base

LOCAL_SQLITE_URL = "sqlite:///./telco_platform.db"


def resolve_database_url() -> str:
    """Resolve the connection URL using the configuration contract's order.

    1. ``TELECO_DB_URL`` is used verbatim when set to a non-empty value.
    2. Otherwise ``dev`` and ``test`` use the local SQLite URL.
    3. Otherwise the URL is composed from the ``TELECO_DB_*`` components.

    Returns:
        The resolved connection URL.
    """
    explicit = os.environ.get("TELECO_DB_URL", "").strip()
    if explicit:
        return explicit

    environment = os.environ.get("TELECO_ENV", "").strip()
    if environment in {"dev", "test"}:
        return LOCAL_SQLITE_URL

    user = os.environ.get("TELECO_DB_USER", "") or "telco_app"
    password = os.environ.get("TELECO_DB_PASSWORD", "")
    host = os.environ.get("TELECO_DB_HOST", "") or "127.0.0.1"
    port = os.environ.get("TELECO_DB_PORT", "") or "5432"
    name = os.environ.get("TELECO_DB_NAME", "") or "telco_si"
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


SQLALCHEMY_DATABASE_URL = resolve_database_url()

_IS_SQLITE = SQLALCHEMY_DATABASE_URL.startswith("sqlite")
_IS_MEMORY = SQLALCHEMY_DATABASE_URL in {"sqlite://", "sqlite:///:memory:"}

_engine_kwargs: dict[str, Any] = {}
if _IS_SQLITE:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
if _IS_MEMORY:
    # An in-memory database exists only for the lifetime of one connection,
    # so every session must share the same one.
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(SQLALCHEMY_DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all() -> None:
    """Create any missing tables for the configured database."""
    Base.metadata.create_all(bind=engine)


__all__ = [
    "Base",
    "SQLALCHEMY_DATABASE_URL",
    "SessionLocal",
    "create_all",
    "engine",
    "get_db",
    "resolve_database_url",
]
