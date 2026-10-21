"""Alembic environment for the telco platform.

Uses the shared declarative metadata from ``src.models`` so that autogenerate
observes the same registry as runtime queries.
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
from src.models import Base  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This is useful to generate SQL scripts without connecting to a database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with Alembic.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
