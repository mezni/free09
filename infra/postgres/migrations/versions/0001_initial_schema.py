
"""Create initial telecom schemas and core tables."""

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA iam")
    op.execute("CREATE SCHEMA crm")
    op.execute("CREATE SCHEMA catalog")
    op.execute("CREATE SCHEMA subscription")
    op.execute("CREATE SCHEMA device")
    op.execute("CREATE SCHEMA billing")
    op.execute("CREATE SCHEMA support")
    op.execute("CREATE SCHEMA audit")

    op.execute("""
        CREATE TABLE iam.users (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            role VARCHAR(20) NOT NULL
                CHECK (role IN ('AGENT', 'SUPERVISOR', 'AI_BOT')),
            password_hash VARCHAR(255),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE crm.customers (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            customer_number VARCHAR(30) NOT NULL UNIQUE,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(254) NOT NULL UNIQUE,
            phone VARCHAR(30),
            status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
                CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE catalog.products (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            product_code VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(150) NOT NULL,
            product_type VARCHAR(30) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        )
    """)

    op.execute("""
        CREATE TABLE catalog.plans (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            product_id BIGINT NOT NULL
                REFERENCES catalog.products(id),
            plan_code VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(150) NOT NULL,
            monthly_price NUMERIC(12, 2) NOT NULL
                CHECK (monthly_price >= 0),
            data_allowance_gb NUMERIC(12, 2)
                CHECK (data_allowance_gb IS NULL OR data_allowance_gb >= 0),
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        )
    """)

    op.execute("""
        CREATE TABLE catalog.addons (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            addon_code VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(150) NOT NULL,
            monthly_price NUMERIC(12, 2) NOT NULL
                CHECK (monthly_price >= 0),
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        )
    """)

    op.execute("""
        CREATE TABLE subscription.subscriptions (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            subscription_number VARCHAR(40) NOT NULL UNIQUE,
            customer_id BIGINT NOT NULL REFERENCES crm.customers(id),
            plan_id BIGINT NOT NULL REFERENCES catalog.plans(id),
            status VARCHAR(20) NOT NULL
                CHECK (status IN (
                    'PENDING', 'ACTIVE', 'SUSPENDED', 'CANCELLED'
                )),
            start_date DATE NOT NULL,
            end_date DATE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CHECK (end_date IS NULL OR end_date >= start_date)
        )
    """)

    op.execute("""
        CREATE TABLE subscription.subscription_addons (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            subscription_id BIGINT NOT NULL
                REFERENCES subscription.subscriptions(id),
            addon_id BIGINT NOT NULL REFERENCES catalog.addons(id),
            start_date DATE NOT NULL,
            end_date DATE,
            CHECK (end_date IS NULL OR end_date >= start_date),
            UNIQUE (subscription_id, addon_id, start_date)
        )
    """)

    op.execute("""
        CREATE TABLE device.devices (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            device_identifier VARCHAR(80) NOT NULL UNIQUE,
            subscription_id BIGINT NOT NULL
                REFERENCES subscription.subscriptions(id),
            device_type VARCHAR(30) NOT NULL,
            status VARCHAR(20) NOT NULL
                CHECK (status IN (
                    'ACTIVE', 'INACTIVE', 'BLOCKED', 'PENDING'
                )),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE billing.invoices (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            invoice_number VARCHAR(40) NOT NULL UNIQUE,
            customer_id BIGINT NOT NULL REFERENCES crm.customers(id),
            subscription_id BIGINT
                REFERENCES subscription.subscriptions(id),
            issue_date DATE NOT NULL,
            due_date DATE NOT NULL,
            total_amount NUMERIC(12, 2) NOT NULL
                CHECK (total_amount >= 0),
            amount_paid NUMERIC(12, 2) NOT NULL DEFAULT 0
                CHECK (amount_paid >= 0 AND amount_paid <= total_amount),
            status VARCHAR(20) NOT NULL
                CHECK (status IN (
                    'DRAFT', 'ISSUED', 'PARTIALLY_PAID',
                    'PAID', 'OVERDUE', 'VOID'
                )),
            CHECK (due_date >= issue_date)
        )
    """)

    op.execute("""
        CREATE TABLE billing.invoice_items (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            invoice_id BIGINT NOT NULL
                REFERENCES billing.invoices(id) ON DELETE CASCADE,
            description VARCHAR(255) NOT NULL,
            quantity NUMERIC(12, 2) NOT NULL CHECK (quantity > 0),
            unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
            line_total NUMERIC(12, 2) NOT NULL CHECK (line_total >= 0)
        )
    """)

    op.execute("""
        CREATE TABLE billing.payments (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            payment_reference VARCHAR(60) NOT NULL UNIQUE,
            customer_id BIGINT NOT NULL REFERENCES crm.customers(id),
            amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
            payment_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            status VARCHAR(20) NOT NULL
                CHECK (status IN (
                    'PENDING', 'COMPLETED', 'FAILED', 'REFUNDED'
                ))
        )
    """)

    op.execute("""
        CREATE TABLE billing.payment_allocations (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            payment_id BIGINT NOT NULL
                REFERENCES billing.payments(id),
            invoice_id BIGINT NOT NULL
                REFERENCES billing.invoices(id),
            amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
            UNIQUE (payment_id, invoice_id)
        )
    """)

    op.execute("""
        CREATE TABLE support.tickets (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            ticket_number VARCHAR(40) NOT NULL UNIQUE,
            customer_id BIGINT NOT NULL REFERENCES crm.customers(id),
            subscription_id BIGINT
                REFERENCES subscription.subscriptions(id),
            category VARCHAR(50) NOT NULL,
            priority VARCHAR(20) NOT NULL
                CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
            status VARCHAR(20) NOT NULL
                CHECK (status IN (
                    'OPEN', 'IN_PROGRESS', 'PENDING', 'RESOLVED', 'CLOSED'
                )),
            subject VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE audit.audit_logs (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            actor_type VARCHAR(20) NOT NULL
                CHECK (actor_type IN ('USER', 'AI_BOT', 'SYSTEM')),
            actor_id BIGINT,
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(100) NOT NULL,
            resource_id VARCHAR(100),
            outcome VARCHAR(20) NOT NULL
                CHECK (outcome IN ('SUCCESS', 'DENIED', 'FAILURE')),
            details JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX ix_subscriptions_customer
        ON subscription.subscriptions(customer_id)
    """)
    op.execute("""
        CREATE INDEX ix_subscriptions_plan
        ON subscription.subscriptions(plan_id)
    """)
    op.execute("""
        CREATE INDEX ix_devices_subscription
        ON device.devices(subscription_id)
    """)
    op.execute("""
        CREATE INDEX ix_invoices_customer_status
        ON billing.invoices(customer_id, status)
    """)
    op.execute("""
        CREATE INDEX ix_tickets_customer_status
        ON support.tickets(customer_id, status)
    """)
    op.execute("""
        CREATE INDEX ix_audit_logs_created_at
        ON audit.audit_logs(created_at)
    """)


def downgrade() -> None:
    for schema in (
        "audit",
        "support",
        "billing",
        "device",
        "subscription",
        "catalog",
        "crm",
        "iam",
    ):
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")

