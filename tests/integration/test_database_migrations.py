"""The migration and schema checks for the four domain schemas.

These checks need a live PostgreSQL instance. The `test` check establishes
that the instance is there before the suite runs (`ci/check_database.py`);
without it the check reports *could not run* rather than passing quietly
(Art. VII.3).

What they assert:

* the migration set applies to an empty database, from the first revision to
  the head, without manual intervention (NFR-031);
* the schema it produces is the documented one (NFR-030);
* the set is reversible (SC-033);
* the set has a single head, so no two revisions compete;
* no foreign key crosses a schema boundary (D-04);
* the grant separation the configuration contract requires holds: a domain
  role may write its own schema and no other (D-04, ADR-0001).
"""

import re
from pathlib import Path

import psycopg
import pytest
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from src.models.telco import TelcoBase

from .database_harness import (
    alembic_config,
    apply_migrations,
    revert_migrations,
    role_url,
)

pytestmark = pytest.mark.database

DOMAIN_SCHEMAS = ("auth", "crm", "inventory", "billing")
DATA_MODEL = (
    Path(__file__).resolve().parents[2] / "specs" / "003-build-phase2" / "data-model.md"
)

INSERT_CUSTOMER = """
    insert into crm.customer (
        id, external_reference, legal_name, customer_type, created_by, updated_by
    ) values (
        gen_random_uuid(), 'EXT-CHECK', 'Check Ltd', 'organization',
        gen_random_uuid(), gen_random_uuid()
    )
"""

INSERT_INVOICE = """
    insert into billing.invoice (
        id, billing_account_id, invoice_number, status, currency_code,
        period_start, period_end, created_by, updated_by
    ) values (
        gen_random_uuid(), gen_random_uuid(), 'INV-CHECK', 'draft', 'EUR',
        now(), now(), gen_random_uuid(), gen_random_uuid()
    )
"""

FOREIGN_KEYS = """
    select source_namespace.nspname as source_schema,
           target_namespace.nspname as target_schema,
           source.relname as source_table
    from pg_constraint constraint_row
    join pg_class source on source.oid = constraint_row.conrelid
    join pg_namespace source_namespace
      on source_namespace.oid = source.relnamespace
    join pg_class target on target.oid = constraint_row.confrelid
    join pg_namespace target_namespace
      on target_namespace.oid = target.relnamespace
    where constraint_row.contype = 'f'
"""


def documented_tables() -> set[str]:
    """Return the tables the data dictionary names."""
    content = DATA_MODEL.read_text(encoding="utf-8")
    return set(re.findall(r"^#### `([a-z]+\.[a-z_]+)`", content, flags=re.MULTILINE))


def test_migration_set_applies_to_an_empty_database(scratch_database: str) -> None:
    """The whole set applies from the first revision to the head (NFR-031)."""
    apply_migrations(scratch_database, "head")

    engine = create_engine(scratch_database)
    with engine.connect() as connection:
        applied = connection.execute(
            text("select version_num from alembic_version")
        ).scalar_one()

    script = ScriptDirectory.from_config(alembic_config())
    assert applied == script.get_current_head()


def test_migration_set_has_a_single_head() -> None:
    """One head means one forward path (NFR-031)."""
    script = ScriptDirectory.from_config(alembic_config())
    assert len(script.get_heads()) == 1


def test_migrated_schema_matches_the_documented_model(scratch_database: str) -> None:
    """The migrated schema is the documented one (NFR-030)."""
    apply_migrations(scratch_database, "head")

    engine = create_engine(scratch_database)
    inspector = inspect(engine)

    migrated = {
        f"{schema}.{table}"
        for schema in DOMAIN_SCHEMAS
        for table in inspector.get_table_names(schema=schema)
    }
    assert migrated == set(TelcoBase.metadata.tables)

    for name, table in TelcoBase.metadata.tables.items():
        schema, table_name = name.split(".")
        columns = {
            column["name"]
            for column in inspector.get_columns(table_name, schema=schema)
        }
        assert columns == {column.name for column in table.columns}


def test_documented_tables_match_the_migrated_schema(scratch_database: str) -> None:
    """The data dictionary names exactly the tables that are migrated."""
    apply_migrations(scratch_database, "head")

    engine = create_engine(scratch_database)
    inspector = inspect(engine)

    migrated = {
        f"{schema}.{table}"
        for schema in DOMAIN_SCHEMAS
        for table in inspector.get_table_names(schema=schema)
    }
    assert migrated == documented_tables()


def test_migration_set_is_reversible(scratch_database: str) -> None:
    """Every revision states a rollback, and the set rolls back (SC-033)."""
    apply_migrations(scratch_database, "head")
    revert_migrations(scratch_database, "base")

    engine = create_engine(scratch_database)
    inspector = inspect(engine)
    for schema in DOMAIN_SCHEMAS:
        assert inspector.get_table_names(schema=schema) == []


def test_no_foreign_key_crosses_a_schema(scratch_database: str) -> None:
    """No table references another domain's table (D-04)."""
    apply_migrations(scratch_database, "head")

    engine = create_engine(scratch_database)
    with engine.connect() as connection:
        foreign_keys = connection.execute(text(FOREIGN_KEYS)).all()

    crossings = [
        (source, target, table)
        for source, target, table in foreign_keys
        if source != target
    ]
    assert crossings == []


def test_crm_role_cannot_write_billing_schema(scratch_database: str) -> None:
    """A domain role writes its own schema and no other (ADR-0001, D-04)."""
    apply_migrations(scratch_database, "head")

    crm = role_url(scratch_database, "telco_crm")
    with psycopg.connect(crm, autocommit=True) as connection:
        connection.execute(INSERT_CUSTOMER)

        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute(INSERT_INVOICE)
