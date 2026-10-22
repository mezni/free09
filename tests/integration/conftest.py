"""Fixtures for the migration and schema checks.

Every check works on its own scratch database: the fixture creates it,
applies the environment's roles and grants, and drops the database again
when the check is done. The database a developer works in is never touched.

The roles are cluster-level objects, so they are shared by every scratch
database; the schemas and the grants are created per database by the same
script the local compose topology uses.
"""

import uuid
from typing import Iterator

import psycopg
import pytest
from psycopg import sql
from sqlalchemy.engine import make_url

from ci.database import migration_database_url

from .database_harness import INIT_SCRIPT


@pytest.fixture
def scratch_database() -> Iterator[str]:
    """Yield the URL of an empty database with the roles and grants applied."""
    admin = make_url(migration_database_url())
    name = f"telco_migration_{uuid.uuid4().hex[:12]}"

    with psycopg.connect(
        admin.render_as_string(hide_password=False), autocommit=True
    ) as connection:
        connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    try:
        with psycopg.connect(
            admin.set(database=name).render_as_string(hide_password=False),
            autocommit=True,
        ) as connection:
            connection.execute(INIT_SCRIPT.read_text(encoding="utf-8"))
        yield admin.set(database=name).render_as_string(hide_password=False)
    finally:
        with psycopg.connect(
            admin.render_as_string(hide_password=False), autocommit=True
        ) as connection:
            connection.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                    sql.Identifier(name)
                )
            )
