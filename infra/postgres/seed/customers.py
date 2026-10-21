
from faker import Faker
from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.engine import Engine

from infra.postgres.seed.config import SEED

CUSTOMER_COUNT = 20


def build_customer_records(count: int = CUSTOMER_COUNT) -> list[dict]:
    """Generate repeatable synthetic customer records."""
    fake = Faker("en_CA")
    fake.seed_instance(SEED)

    records = []

    for number in range(1, count + 1):
        records.append(
            {
                "customer_number": f"TEL-{number:06d}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": f"customer{number:06d}@example.test",
                "phone": fake.phone_number()[:30],
                "status": "ACTIVE",
            }
        )

    return records


def seed_customers(engine: Engine) -> int:
    """Insert missing CRM customers and return the number inserted."""
    with engine.begin() as connection:
        inspector = inspect(connection)

        if "customers" not in inspector.get_table_names(schema="crm"):
            raise RuntimeError(
                "Table crm.customers does not exist. "
                "Run Alembic migrations first."
            )

        customers = Table(
            "customers",
            MetaData(),
            schema="crm",
            autoload_with=connection,
        )

        existing_numbers = set(
            connection.execute(
                select(customers.c.customer_number)
            ).scalars()
        )

        existing_emails = set(
            connection.execute(
                select(customers.c.email)
            ).scalars()
        )

        inserted = 0

        for record in build_customer_records():
            if (
                record["customer_number"] in existing_numbers
                or record["email"] in existing_emails
            ):
                continue

            connection.execute(customers.insert().values(**record))
            existing_numbers.add(record["customer_number"])
            existing_emails.add(record["email"])
            inserted += 1

        return inserted

