"""Harness for the migration and schema checks.

The helpers here drive Alembic in-process and address the domain roles. The
fixture that hands each check its own scratch database lives in
`tests/integration/conftest.py`.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import make_url

from ci.database import PLACEHOLDER_MARKER

REPO_ROOT = Path(__file__).resolve().parents[2]
INIT_SCRIPT = REPO_ROOT / "deploy" / "compose" / "initdb" / "001_schemas_and_roles.sql"
ALEMBIC_INI = REPO_ROOT / "alembic.ini"
MIGRATIONS_DIR = REPO_ROOT / "migrations"


def alembic_config(database_url: str | None = None) -> Config:
    """Return an Alembic configuration rooted at this repository."""
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    if database_url:
        config.set_main_option("sqlalchemy.url", database_url)
    return config


def apply_migrations(database_url: str, target: str = "head") -> None:
    """Apply the migration set to the given database."""
    command.upgrade(alembic_config(database_url), target)


def revert_migrations(database_url: str, target: str = "base") -> None:
    """Revert the migration set on the given database."""
    command.downgrade(alembic_config(database_url), target)


def role_url(database_url: str, role: str) -> str:
    """Return the URL a domain role connects with."""
    url = make_url(database_url).set(username=role).set(password=PLACEHOLDER_MARKER)
    return url.render_as_string(hide_password=False)
