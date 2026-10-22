"""The `inventory` schema — owned by `inventory-service`.

The commercial catalogue (products, rate plans, add-ons), the subscriptions
held on those rate plans, the physical assets (devices, SIMs), and
provisioning (FR-035). The schema is `Internal` (D-10): only
`inventory-service` writes it.

The catalogue is the platform's shared reference data, and `inventory-service`
is its single owner (D-02): `crm-service`, `billing-service`, and
`auth-service` read it through the inventory API, never through a shared table
and never through a cross-schema foreign key (D-04).

See `specs/003-build-phase2/data-model.md` §3.3 for the dictionary this
module realises.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CHAR,
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

SCHEMA = "inventory"


class Product(AuditMixin, TelcoBase):
    """`inventory.product` — a sellable thing, or a family of them."""

    __tablename__ = "product"
    __table_args__ = (
        Index("ix_inventory_product_type_status", "product_type", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    product_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(String(24), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="draft", server_default="draft"
    )


class ProductVersion(AuditMixin, TelcoBase):
    """`inventory.product_version` — a versioned definition of a product."""

    __tablename__ = "product_version"
    __table_args__ = (
        Index(
            "uq_inventory_product_version_number",
            "product_id",
            "version_number",
            unique=True,
        ),
        Index(
            "uq_inventory_product_version_current",
            "product_id",
            unique=True,
            postgresql_where=text("valid_to IS NULL"),
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.product.id", ondelete="RESTRICT"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    definition: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class RatePlan(AuditMixin, TelcoBase):
    """`inventory.rate_plan` — the commercial plan a subscription is held on."""

    __tablename__ = "rate_plan"
    __table_args__ = ({"schema": SCHEMA},)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.product.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    plan_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    billing_interval: Mapped[str] = mapped_column(String(16), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)


class RatePlanVersion(AuditMixin, TelcoBase):
    """`inventory.rate_plan_version` — the priced terms of a rate plan."""

    __tablename__ = "rate_plan_version"
    __table_args__ = (
        Index(
            "uq_inventory_rate_plan_version_number",
            "rate_plan_id",
            "version_number",
            unique=True,
        ),
        Index(
            "uq_inventory_rate_plan_version_current",
            "rate_plan_id",
            unique=True,
            postgresql_where=text("valid_to IS NULL"),
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    rate_plan_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.rate_plan.id", ondelete="RESTRICT"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    base_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    quota: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    terms: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class AddOn(AuditMixin, TelcoBase):
    """`inventory.add_on` — an optional product attached to a subscription."""

    __tablename__ = "add_on"
    __table_args__ = ({"schema": SCHEMA},)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.product.id", ondelete="RESTRICT"),
        nullable=False,
    )
    add_on_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    billing_interval: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)


class Subscription(AuditMixin, TelcoBase):
    """`inventory.subscription` — what a subscriber holds."""

    __tablename__ = "subscription"
    __table_args__ = (
        Index("ix_inventory_subscription_subscriber_status", "subscriber_id", "status"),
        Index("ix_inventory_subscription_valid_from", "valid_from"),
        Index("ix_inventory_subscription_rate_plan_status", "rate_plan_id", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    subscriber_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    rate_plan_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.rate_plan.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    pricing_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )


class SubscriptionAddOn(AuditMixin, TelcoBase):
    """`inventory.subscription_add_on` — an add-on on a subscription."""

    __tablename__ = "subscription_add_on"
    __table_args__ = (
        Index(
            "uq_inventory_subscription_add_on",
            "subscription_id",
            "add_on_id",
            "valid_from",
            unique=True,
        ),
        Index(
            "ix_inventory_subscription_add_on_subscription_status",
            "subscription_id",
            "status",
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    subscription_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.subscription.id", ondelete="RESTRICT"),
        nullable=False,
    )
    add_on_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.add_on.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Device(AuditMixin, TelcoBase):
    """`inventory.device` — a physical device."""

    __tablename__ = "device"
    __table_args__ = (
        Index(
            "uq_inventory_device_imei",
            "imei",
            unique=True,
            postgresql_where=text("imei IS NOT NULL"),
        ),
        Index("ix_inventory_device_status", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    serial_number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    imei: Mapped[str | None] = mapped_column(String(20), nullable=True)
    device_type: Mapped[str] = mapped_column(String(48), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    acquired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class DeviceAssignment(AuditMixin, TelcoBase):
    """`inventory.device_assignment` — who holds a device, and for how long."""

    __tablename__ = "device_assignment"
    __table_args__ = (
        Index(
            "ix_inventory_device_assignment_device_assigned_at",
            "device_id",
            "assigned_at",
        ),
        Index("ix_inventory_device_assignment_subscriber_id", "subscriber_id"),
        Index(
            "uq_inventory_device_assignment_current",
            "device_id",
            unique=True,
            postgresql_where=text("released_at IS NULL"),
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.device.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subscriber_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    subscription_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("inventory.subscription.id", ondelete="RESTRICT"),
        nullable=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(String(32), nullable=True)


class Sim(AuditMixin, TelcoBase):
    """`inventory.sim` — a SIM identity."""

    __tablename__ = "sim"
    __table_args__ = (
        Index(
            "uq_inventory_sim_msisdn",
            "msisdn",
            unique=True,
            postgresql_where=text("msisdn IS NOT NULL"),
        ),
        Index("ix_inventory_sim_status", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    iccid: Mapped[str] = mapped_column(String(24), nullable=False, unique=True)
    sim_type: Mapped[str] = mapped_column(String(16), nullable=False)
    msisdn: Mapped[str | None] = mapped_column(String(32), nullable=True)
    carrier: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("inventory.device.id", ondelete="RESTRICT"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False)


class SimAssignment(AuditMixin, TelcoBase):
    """`inventory.sim_assignment` — who holds a SIM, and for how long."""

    __tablename__ = "sim_assignment"
    __table_args__ = (
        Index("ix_inventory_sim_assignment_sim_assigned_at", "sim_id", "assigned_at"),
        Index("ix_inventory_sim_assignment_subscriber_id", "subscriber_id"),
        Index(
            "uq_inventory_sim_assignment_current",
            "sim_id",
            unique=True,
            postgresql_where=text("released_at IS NULL"),
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    sim_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.sim.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subscriber_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    subscription_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("inventory.subscription.id", ondelete="RESTRICT"),
        nullable=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ProvisioningProfile(AuditMixin, TelcoBase):
    """`inventory.provisioning_profile` — the template a job applies."""

    __tablename__ = "provisioning_profile"
    __table_args__ = ({"schema": SCHEMA},)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    profile_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    apn: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parameters: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)


class ProvisioningJob(AuditMixin, TelcoBase):
    """`inventory.provisioning_job` — a request to change a service."""

    __tablename__ = "provisioning_job"
    __table_args__ = (
        Index(
            "ix_inventory_provisioning_job_subscription_status",
            "subscription_id",
            "status",
        ),
        Index("ix_inventory_provisioning_job_status", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    subscription_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.subscription.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subscriber_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    profile_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("inventory.provisioning_profile.id", ondelete="RESTRICT"),
        nullable=False,
    )
    job_type: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True
    )
    attempt_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    failure_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
