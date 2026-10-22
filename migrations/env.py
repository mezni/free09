"""Alembic environment for the telco platform.

The migration set is built from the four domain schemas declared in
`src.models.telco`, so that autogenerate observes exactly the metadata the
runtime queries use (FR-036, NFR-038).

The connection URL is resolved in one order, and nowhere else:

1. the `sqlalchemy.url` main option, when it is set — this is how the
   schema checks apply the migration set to a scratch database;
2. `TELECO_MIGRATION_DB_URL`, the connection the migration tool uses;
3. the `TELECO_DB_*` components (host, port, name, user, password).

`TELECO_DB_URL` is deliberately not consulted: it carries the running
service's connection, which may be a local SQLite file.

Setting `TELECO_AUTOGENERATE_DOMAIN` to a schema name restricts
autogenerate to that domain, so that one revision can be produced per owning
service. The variable affects autogenerate only; it changes nothing at
upgrade or downgrade time.
"""

import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# add repository root to path so we can import the `src` package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import model metadata for autogenerate support
from src.models.telco import TelcoBase  # noqa: E402

target_metadata = TelcoBase.metadata

AUTOGENERATE_DOMAIN = os.environ.get("TELECO_AUTOGENERATE_DOMAIN", "").strip()


def _object_schema(obj: object) -> str | None:
    """Return the schema an Alembic object belongs to, if it has one."""
    table = getattr(obj, "table", None)
    if table is not None:
        return getattr(table, "schema", None)
    return getattr(obj, "schema", None)


def _include_object(obj, name, type_, reflected, compare_to) -> bool:
    """Restrict autogenerate to one domain when a domain is selected."""
    if not AUTOGENERATE_DOMAIN:
        return True
    return _object_schema(obj) == AUTOGENERATE_DOMAIN


def resolve_url() -> str:
    """Resolve the database URL the migration set is applied to."""
    configured = config.get_main_option("sqlalchemy.url", None)
    if configured:
        return configured

    migration_url = os.environ.get("TELECO_MIGRATION_DB_URL", "").strip()
    if migration_url:
        return migration_url

    host = os.environ.get("TELECO_DB_HOST", "") or "127.0.0.1"
    port = os.environ.get("TELECO_DB_PORT", "") or "5432"
    name = os.environ.get("TELECO_DB_NAME", "") or "telco_si"
    user = os.environ.get("TELECO_DB_USER", "") or "telco_app"
    password = os.environ.get("TELECO_DB_PASSWORD", "")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This is useful to generate SQL scripts without connecting to a database.
    """
    url = resolve_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=_include_object,
        version_table="alembic_version",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with Alembic.
    """
    connectable = engine_from_config(
        {"sqlalchemy.url": resolve_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=_include_object,
            version_table="alembic_version",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
