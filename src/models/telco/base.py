"""Shared conventions for the four domain schemas.

The domain schemas (`auth`, `crm`, `inventory`, `billing`) live on their own
declarative base, separate from the platform application's `src.models.Base`.
The two registries keep independent lifecycles: the application tables are
created by `src.database.create_all()`, while the domain schemas are created
only by the migration set under `migrations/versions/` (FR-036, NFR-030).

See `specs/003-build-phase2/data-model.md` §2 for the rules every table
follows, and `specs/003-build-phase2/research.md` for the decisions these
conventions implement (D-05 keys, D-06 audit fields, D-07 money, D-08 time).
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Integer, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TelcoBase(DeclarativeBase):
    """Declarative base for the four domain schemas."""


class AuditMixin:
    """The audit fields every domain table carries (D-06).

    `created_at` and `updated_at` are server-defaulted to the transaction
    timestamp; `created_by` and `updated_by` carry the identifier of the
    principal that made the change; `version` is the optimistic-locking
    counter. There is no soft delete (D-09): a row is removed or it is not.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
    )
    created_by: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    updated_by: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
