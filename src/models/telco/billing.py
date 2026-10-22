"""The `billing` schema — owned by `billing-service`.

Billing accounts, invoices, payments, allocations, credit memos, and the
double-entry ledger (FR-036). The schema is `Restricted` (D-10): only
`billing-service` writes it.

Money is `numeric(19, 4)` and always carries its ISO 4217 currency code
(D-07); there is no floating-point money anywhere in this schema.

See `specs/003-build-phase2/data-model.md` §3.4 for the dictionary this
module realises.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CHAR,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.telco.base import AuditMixin, TelcoBase

SCHEMA = "billing"


class BillingAccount(AuditMixin, TelcoBase):
    """`billing.billing_account` — the entity an invoice is issued to."""

    __tablename__ = "billing_account"
    __table_args__ = (
        Index("ix_billing_billing_account_customer_status", "customer_id", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    account_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    billing_cycle_day: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_terms_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Invoice(AuditMixin, TelcoBase):
    """`billing.invoice` — a statement of what was owed."""

    __tablename__ = "invoice"
    __table_args__ = (
        Index("ix_billing_invoice_account_status", "billing_account_id", "status"),
        Index("ix_billing_invoice_status_due_date", "status", "due_date"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    billing_account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.billing_account.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subscriber_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    invoice_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False, default=Decimal("0"), server_default="0"
    )
    tax_total: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False, default=Decimal("0"), server_default="0"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False, default=Decimal("0"), server_default="0"
    )
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    voided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class InvoiceLine(AuditMixin, TelcoBase):
    """`billing.invoice_line` — one charge on an invoice, priced as it was."""

    __tablename__ = "invoice_line"
    __table_args__ = (
        Index("ix_billing_invoice_line_invoice_id", "invoice_id"),
        Index("ix_billing_invoice_line_product_code", "product_code"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    invoice_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.invoice.id", ondelete="RESTRICT"),
        nullable=False,
    )
    line_type: Mapped[str] = mapped_column(String(24), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    product_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rate_plan_version_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False, default=Decimal("1"), server_default="1"
    )
    unit_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    tax_rate: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False, default=Decimal("0"), server_default="0"
    )
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    price_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Payment(AuditMixin, TelcoBase):
    """`billing.payment` — money received."""

    __tablename__ = "payment"
    __table_args__ = (
        Index("ix_billing_payment_account_status", "billing_account_id", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    billing_account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.billing_account.id", ondelete="RESTRICT"),
        nullable=False,
    )
    payment_reference: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    captured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class PaymentAllocation(AuditMixin, TelcoBase):
    """`billing.payment_allocation` — the part of a payment applied to an invoice."""

    __tablename__ = "payment_allocation"
    __table_args__ = (
        Index("ix_billing_payment_allocation_payment_id", "payment_id"),
        Index("ix_billing_payment_allocation_invoice_id", "invoice_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    payment_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.payment.id", ondelete="RESTRICT"),
        nullable=False,
    )
    invoice_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.invoice.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    allocated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )


class CreditMemo(AuditMixin, TelcoBase):
    """`billing.credit_memo` — a credit issued against an invoice."""

    __tablename__ = "credit_memo"
    __table_args__ = (
        Index("ix_billing_credit_memo_account_status", "billing_account_id", "status"),
        Index("ix_billing_credit_memo_invoice_id", "invoice_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    credit_memo_number: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True
    )
    billing_account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.billing_account.id", ondelete="RESTRICT"),
        nullable=False,
    )
    invoice_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.invoice.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    requested_by: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    approved_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rejected_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class LedgerAccount(AuditMixin, TelcoBase):
    """`billing.ledger_account` — a posting destination."""

    __tablename__ = "ledger_account"
    __table_args__ = ({"schema": SCHEMA},)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    account_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    account_type: Mapped[str] = mapped_column(String(16), nullable=False)
    normal_balance: Mapped[str] = mapped_column(String(8), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )


class LedgerEntryGroup(AuditMixin, TelcoBase):
    """`billing.ledger_entry_group` — the postings of one financial event."""

    __tablename__ = "ledger_entry_group"
    __table_args__ = (
        Index("ix_billing_ledger_entry_group_source", "source_type", "source_id"),
        Index("ix_billing_ledger_entry_group_correlation_id", "correlation_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_type: Mapped[str] = mapped_column(String(48), nullable=False)
    source_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)


class LedgerEntry(AuditMixin, TelcoBase):
    """`billing.ledger_entry` — one posting. Append-only and immutable."""

    __tablename__ = "ledger_entry"
    __table_args__ = (
        Index(
            "ix_billing_ledger_entry_account_occurred_at",
            "ledger_account_id",
            "occurred_at",
        ),
        Index("ix_billing_ledger_entry_entry_group_id", "entry_group_id"),
        Index("ix_billing_ledger_entry_correlation_id", "correlation_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    entry_group_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.ledger_entry_group.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ledger_account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("billing.ledger_account.id", ondelete="RESTRICT"),
        nullable=False,
    )
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)


class TaxRate(AuditMixin, TelcoBase):
    """`billing.tax_rate` — the tax rate that applied in a jurisdiction."""

    __tablename__ = "tax_rate"
    __table_args__ = (
        Index(
            "uq_billing_tax_rate_jurisdiction_type_from",
            "jurisdiction_code",
            "tax_type",
            "valid_from",
            unique=True,
        ),
        Index(
            "uq_billing_tax_rate_current",
            "jurisdiction_code",
            "tax_type",
            unique=True,
            postgresql_where=text("valid_to IS NULL"),
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    jurisdiction_code: Mapped[str] = mapped_column(String(16), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(32), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    currency_code: Mapped[str | None] = mapped_column(CHAR(3), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
