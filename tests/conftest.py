"""Conftest.py — Shared fixtures and marker registration for telco platform."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# The test suite runs against an in-memory database. This must be set before
# `src.database` is imported, because the engine is created at import time.
os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite://")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, cross-component)"
    )
    config.addinivalue_line(
        "markers", "contract: Contract tests (API surface validation)"
    )
    config.addinivalue_line(
        "markers",
        "governance: Governance-related tests (constitution, ADRs, templates)",
    )
    config.addinivalue_line(
        "markers", "slow: Marks that require significant time or resources"
    )
    config.addinivalue_line(
        "markers",
        "minimal_test_suite_passes_on_empty_implementation: "
        "Marker for the always-passing minimal suite",
    )


def pytest_collection_modifyitems(config, items):
    """Optionally reorder or skip items based on markers."""
    pass


@pytest.fixture(scope="session", autouse=True)
def _database_schema():
    """Create the schema for the in-memory test database."""
    from src.database import create_all

    create_all()
    return


@pytest.fixture(autouse=True)
def _reset_database():
    """Reset table contents so tests observe a deterministic starting state."""
    from src.database import SessionLocal
    from src.models import Base

    with SessionLocal() as session:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    return


@pytest.fixture(scope="session")
def clone_dir_fixture(tmp_path_factory):
    """Provide a scratch directory standing in for a fresh clone.

    The directory is empty by design: the governance assertions verify that
    the documented setup path is *available*, not that a clone has already
    been provisioned.
    """
    clone_dir = tmp_path_factory.mktemp("fresh-clone")
    return {"clone_dir": clone_dir}


@pytest.fixture(scope="session")
def tool_bin_fixture():
    """Locate an executable that ships inside the active virtual environment."""
    env_bin = Path(sys.executable).parent

    def _locate(name):
        candidate = env_bin / name
        if candidate.exists():
            return str(candidate)
        return shutil.which(name)

    return _locate


@pytest.fixture(scope="session")
def service_reachable_fixture():
    """Report whether the local API is accepting connections."""
    import urllib.error
    import urllib.request

    def _reachable(url="http://localhost:8000/healthz", timeout=2):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                return response.status < 500
        except (urllib.error.URLError, OSError):
            return False

    return _reachable


def _run(command, **kwargs):
    """Run a command and return the completed process."""
    return subprocess.run(command, capture_output=True, text=True, **kwargs)
