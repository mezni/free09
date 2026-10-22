"""The `auth` schema — owned by `auth-service`.

Identity, access control, credentials, and the security audit trail
(FR-033). The schema is `Restricted` (D-10): only `auth-service` writes it,
and every other domain reaches it through the auth API (D-02, D-04).

See `specs/003-build-phase2/data-model.md` §3.1 for the dictionary this
module realises.
"""

from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.telco.base import AuditMixin, TelcoBase

SCHEMA = "auth"


class User(AuditMixin, TelcoBase):
    """`auth.user` — a principal that can authenticate."""

    __tablename__ = "user"
    __table_args__ = (
        Index("uq_auth_user_email_ci", func.lower(text("email")), unique=True),
        Index("ix_auth_user_status", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending", server_default="pending"
    )
    failed_login_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    token_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )


class Role(AuditMixin, TelcoBase):
    """`auth.role` — a named set of permissions."""

    __tablename__ = "role"
    __table_args__ = ({"schema": SCHEMA},)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )


class Permission(AuditMixin, TelcoBase):
    """`auth.permission` — one action on one resource."""

    __tablename__ = "permission"
    __table_args__ = (
        Index("ix_auth_permission_resource_action", "resource", "action"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(96), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)


class UserRole(AuditMixin, TelcoBase):
    """`auth.user_role` — the grant of a role to a user."""

    __tablename__ = "user_role"
    __table_args__ = (
        Index("ix_auth_user_role_role_id", "role_id"),
        {"schema": SCHEMA},
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("auth.user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("auth.role.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    granted_by: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class RolePermission(AuditMixin, TelcoBase):
    """`auth.role_permission` — the grant of a permission to a role."""

    __tablename__ = "role_permission"
    __table_args__ = ({"schema": SCHEMA},)

    role_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("auth.role.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("auth.permission.id", ondelete="CASCADE"),
        primary_key=True,
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )


class RefreshToken(AuditMixin, TelcoBase):
    """`auth.refresh_token` — a hashed refresh token."""

    __tablename__ = "refresh_token"
    __table_args__ = (
        Index("ix_auth_refresh_token_user_expires_at", "user_id", "expires_at"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("auth.user.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    replaced_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    user_agent_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)


class ServiceCredential(AuditMixin, TelcoBase):
    """`auth.service_credential` — a credential held by another service."""

    __tablename__ = "service_credential"
    __table_args__ = ({"schema": SCHEMA},)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    service_name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    credential_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="active", server_default="active"
    )
    scopes: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        server_default=text("'{}'::text[]"),
    )
    rotated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class SecurityAuditEvent(TelcoBase):
    """`auth.security_audit_event` — the append-only security trail."""

    __tablename__ = "security_audit_event"
    __table_args__ = (
        Index("ix_auth_security_audit_event_actor", "actor_id", "occurred_at"),
        Index("ix_auth_security_audit_event_action", "action", "occurred_at"),
        Index("ix_auth_security_audit_event_correlation_id", "correlation_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    actor_type: Mapped[str] = mapped_column(String(16), nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    action: Mapped[str] = mapped_column(String(96), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_ip: Mapped[IPv4Address | IPv6Address | None] = mapped_column(
        INET, nullable=True
    )
    detail: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
