"""Database helpers shared by the migration checks and the database preflight.

The configuration contract declares one connection for the migration tool and
the schema checks, `TELECO_MIGRATION_DB_URL`. It is resolved here, in one
place, so that the preflight (`ci/check_database.py`) and the checks
themselves never disagree about which database they are talking to.

When the variable is absent the local compose database is used, so that a
developer with `make db-up` running can execute the whole required-check set
without any further setup.
"""

import os

# The local compose topology (deploy/compose/compose.yaml). The password is
# the repository's documented placeholder, which is what the compose file
# itself uses.
DEFAULT_MIGRATION_URL = (
    "postgresql://telco_user:PLACEHOLDER_NO_REAL_CREDENTIAL@127.0.0.1:5432/telco_db"
)

# The marker the repository uses for a placeholder credential. A secret-bearing
# value that still carries it has not been given a real credential.
PLACEHOLDER_MARKER = "PLACEHOLDER_NO_REAL_CREDENTIAL"


def migration_database_url() -> str:
    """Return the connection URL the migration tool and the checks use."""
    return os.environ.get("TELECO_MIGRATION_DB_URL", "").strip() or (
        DEFAULT_MIGRATION_URL
    )


def holds_placeholder(url: str) -> bool:
    """Return True when the URL still carries the placeholder credential."""
    return PLACEHOLDER_MARKER in url


def describe_connection_error(url: str, error: BaseException) -> str:
    """Return a message that names the prerequisite without echoing a secret."""
    host = url.split("@")[-1] if "@" in url else "the configured database"
    return f"the database at {host} could not be reached: {type(error).__name__}"
