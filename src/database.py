"""Database dependency for FastAPI application"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.models import Base

# SQLite for development / PostgreSQL for production
# In production: SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host/db"
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL", "sqlite:///./telco_platform.db"
)

_IS_SQLITE = SQLALCHEMY_DATABASE_URL.startswith("sqlite")
_IS_MEMORY = SQLALCHEMY_DATABASE_URL in {"sqlite://", "sqlite:///:memory:"}

_engine_kwargs: dict = {}
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
]
