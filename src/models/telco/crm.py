"""The `crm` schema — owned by `crm-service`.

Customers, subscribers, contacts, addresses, and the support desk
(FR-034). The schema is `Confidential` (D-10): only `crm-service` writes it.
References to `auth.user` are plain identifiers, not foreign keys (D-04); the
identity service owns that data.

See `specs/003-build-phase2/data-model.md` §3.2 for the dictionary this
module realises.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.models.telco.base import AuditMixin, TelcoBase

SCHEMA = "crm"


class Customer(AuditMixin, TelcoBase):
    """`crm.customer` — the party the operator bills and serves."""

    __tablename__ = "customer"
    __table_args__ = (
        Index("ix_crm_customer_status", "status"),
        Index("ix_crm_customer_legal_name_ci", func.lower(text("legal_name"))),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    external_reference: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_type: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="prospect", server_default="prospect"
    )
    tax_identifier: Mapped[str | None] = mapped_column(String(64), nullable=True)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Contact(AuditMixin, TelcoBase):
    """`crm.contact` — a way to reach a customer."""

    __tablename__ = "contact"
    __table_args__ = (
        Index("ix_crm_contact_customer_id", "customer_id"),
        Index("ix_crm_contact_normalized_value", "normalized_value"),
        Index(
            "uq_crm_contact_primary_per_type",
            "customer_id",
            "contact_type",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("crm.customer.id", ondelete="RESTRICT"),
        nullable=False,
    )
    contact_type: Mapped[str] = mapped_column(String(16), nullable=False)
    contact_value: Mapped[str] = mapped_column(String(320), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(320), nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="active", server_default="active"
    )


class Address(AuditMixin, TelcoBase):
    """`crm.address` — a postal address of a customer, over a period."""

    __tablename__ = "address"
    __table_args__ = (
        Index("ix_crm_address_customer_valid_from", "customer_id", "valid_from"),
        Index("ix_crm_address_country_code", "country_code"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("crm.customer.id", ondelete="RESTRICT"),
        nullable=False,
    )
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    country_code: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    address_type: Mapped[str] = mapped_column(String(16), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Subscriber(AuditMixin, TelcoBase):
    """`crm.subscriber` — the person or machine that holds a service."""

    __tablename__ = "subscriber"
    __table_args__ = (
        Index("ix_crm_subscriber_customer_status", "customer_id", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("crm.customer.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subscriber_number: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    activated_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    terminated_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    suspended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class SubscriberIdentityLink(AuditMixin, TelcoBase):
    """`crm.subscriber_identity_link` — the user account behind a subscriber."""

    __tablename__ = "subscriber_identity_link"
    __table_args__ = (
        Index("ix_crm_subscriber_identity_link_subscriber_id", "subscriber_id"),
        Index("ix_crm_subscriber_identity_link_identity_user_id", "identity_user_id"),
        Index(
            "uq_crm_subscriber_identity_link_primary",
            "subscriber_id",
            unique=True,
            postgresql_where=text("link_type = 'primary' AND unlinked_at IS NULL"),
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    subscriber_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("crm.subscriber.id", ondelete="CASCADE"),
        nullable=False,
    )
    identity_user_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    link_type: Mapped[str] = mapped_column(String(16), nullable=False)
    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    unlinked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class SupportTicket(AuditMixin, TelcoBase):
    """`crm.support_ticket` — a support case."""

    __tablename__ = "support_ticket"
    __table_args__ = (
        Index("ix_crm_support_ticket_customer_status", "customer_id", "status"),
        Index("ix_crm_support_ticket_assigned_agent_id", "assigned_agent_id"),
        Index("ix_crm_support_ticket_opened_at", "opened_at"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("crm.customer.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subscriber_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("crm.subscriber.id", ondelete="RESTRICT"),
        nullable=True,
    )
    ticket_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    priority: Mapped[str] = mapped_column(
        String(16), nullable=False, default="normal", server_default="normal"
    )
    assigned_agent_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TicketStatusHistory(TelcoBase):
    """`crm.ticket_status_history` — the append-only status trail."""

    __tablename__ = "ticket_status_history"
    __table_args__ = (
        Index(
            "ix_crm_ticket_status_history_ticket_changed_at", "ticket_id", "changed_at"
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticket_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("crm.support_ticket.id", ondelete="CASCADE"),
        nullable=False,
    )
    from_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    to_status: Mapped[str] = mapped_column(String(16), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    changed_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class TicketAssignmentHistory(TelcoBase):
    """`crm.ticket_assignment_history` — the append-only assignment trail."""

    __tablename__ = "ticket_assignment_history"
    __table_args__ = (
        Index(
            "ix_crm_ticket_assignment_history_ticket_changed_at",
            "ticket_id",
            "changed_at",
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticket_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("crm.support_ticket.id", ondelete="CASCADE"),
        nullable=False,
    )
    from_agent_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    to_agent_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    changed_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
