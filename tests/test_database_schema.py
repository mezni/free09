
import os

import pytest
from sqlalchemy import create_engine, inspect


@pytest.fixture
def database_inspector():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        pytest.skip("Set DATABASE_URL to run database integration tests")

    engine = create_engine(database_url)

    try:
        yield inspect(engine)
    finally:
        engine.dispose()


def test_required_schemas_exist(database_inspector):
    schemas = set(database_inspector.get_schema_names())

    assert {
        "iam",
        "crm",
        "catalog",
        "subscription",
        "device",
        "billing",
        "support",
        "audit",
    }.issubset(schemas)


def test_core_tables_exist(database_inspector):
    assert database_inspector.has_table("customers", schema="crm")
    assert database_inspector.has_table("subscriptions", schema="subscription")
    assert database_inspector.has_table("invoices", schema="billing")
    assert database_inspector.has_table("tickets", schema="support")

