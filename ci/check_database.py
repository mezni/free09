"""Preflight for the database the schema checks need.

The `test` check runs the migration and schema checks, and those checks need
a live PostgreSQL instance. This preflight establishes that the instance is
there before the suite runs, so that a missing prerequisite is reported as
*could not run* (exit code 2) rather than as a wall of test failures.

Exit codes:

* 0 — the database is reachable;
* 1 — the database is reachable but refused the connection;
* 2 — the database is not reachable, or the connection still carries the
  documented placeholder credential while `TELECO_ENV` is `ci`.
"""

import os
import sys

import psycopg

from ci.database import (
    describe_connection_error,
    holds_placeholder,
    migration_database_url,
)

PASS = 0
FAIL = 1
COULD_NOT_RUN = 2


def main() -> int:
    """Check the database the schema checks need; return the exit code."""
    url = migration_database_url()

    if os.environ.get("TELECO_ENV", "").strip() == "ci" and holds_placeholder(url):
        print("Refusing to run CI checks with placeholder credentials.")
        return COULD_NOT_RUN

    try:
        with psycopg.connect(url, connect_timeout=5):
            pass
    except psycopg.OperationalError as error:
        print(describe_connection_error(url, error))
        print("Start the database with `make db-up`, then run the check again.")
        return COULD_NOT_RUN
    except psycopg.Error as error:
        print(f"the database refused the connection: {type(error).__name__}")
        return FAIL

    return PASS


if __name__ == "__main__":
    sys.exit(main())
