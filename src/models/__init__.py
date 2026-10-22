"""SQLAlchemy declarative base shared by all platform models.

Single source of truth for model metadata so that Alembic autogenerate and
runtime queries observe the same registry.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for every platform model."""
