"""Minimal test suite — passes against an empty implementation.

Test ID: `test_minimal_test_suite_passes_on_empty_implementation`

This test suite is designed to always pass when no real implementation
exists, so that a failing check genuinely indicates a real defect in the
underlying code or configuration.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.governance.helpers import REPO_ROOT

pytestmark = pytest.mark.minimal_test_suite_passes_on_empty_implementation

# The checks that assert a property of the repository rather than of the
# implementation. They must pass on a tree that holds no implementation.
MINIMAL_SUITE = (
    "tests/governance/test_layout_matches_documentation.py",
    "tests/governance/test_templates_unfilled.py",
    "tests/governance/test_templates_no_approved_content.py",
    "tests/governance/test_feature_numbering.py",
    "tests/governance/test_single_constitution.py",
    "tests/governance/test_build_plan.py",
    "tests/governance/test_decision_record_format.py",
    "tests/governance/test_artefact_coverage.py",
    "tests/governance/test_config_agreement.py",
    "tests/governance/test_exit_gate_evidence.py",
    "tests/governance/test_open_questions_owned.py",
    "tests/governance/test_precedence_order.py",
    "tests/governance/test_secret_remediation_procedure.py",
    "tests/governance/test_dependency_review_recorded.py",
    "tests/governance/test_no_runtime_surface.py",
    "tests/governance/test_language_baseline_unchanged.py",
)

# The conftest fixtures that need a database.
DATABASE_SCHEMA_FIXTURE_PATTERN = (
    r'@pytest\.fixture\(scope="session", autouse=True\)\n'
    r"def _database_schema\(\):.*?\n    return\n"
)
RESET_DATABASE_FIXTURE_PATTERN = (
    r"@pytest\.fixture\(autouse=True\)\ndef _reset_database\(\):.*?\n    return\n"
)


@pytest.mark.usefixtures("empty_implementation_fixture")
class TestMinimalSuite:
    """Minimal test suite — see conftest for fixture."""

    def test_minimal_test_suite_passes_on_empty_implementation(self):
        """The minimal suite passes when the implementation is empty.

        The suite is copied into a scratch tree, every implementation module
        is replaced by an empty stub, and the minimal suite is run there. It
        must pass: a check that fails only because a feature is unimplemented
        reports a defect that is not there.
        """
        tree = _empty_implementation_tree()

        result = subprocess.run(
            [sys.executable, "-m", "pytest", *MINIMAL_SUITE, "-q"],
            cwd=tree,
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
            env=_environment(),
        )

        assert result.returncode == 0, (
            "The minimal suite does not pass on an empty implementation:\n"
            f"{result.stdout[-4000:]}"
        )


def _environment() -> dict[str, str]:
    """Return the environment the suite runs with."""
    import os

    return dict(os.environ)


def _empty_implementation_tree(root: Path | None = None) -> Path:
    """Return a copy of the tree whose implementation modules are empty.

    The copy keeps the repository layout, the configuration, and the
    governance suite; it replaces every implementation module with an empty
    stub and drops the fixtures that need a database, so that running the
    suite exercises the checks alone.
    """
    import tempfile

    source = root or REPO_ROOT
    destination = Path(tempfile.mkdtemp(prefix="empty-implementation-"))

    shutil.copytree(
        source,
        destination / "repo",
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            ".nox",
            ".opencode",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "*.egg-info",
            ".env",
            "node_modules",
        ),
        symlinks=True,
    )
    tree = destination / "repo"

    # Empty every implementation module.
    for pattern in ("src", "libs", "services"):
        for module in sorted((tree / pattern).rglob("*.py")):
            module.write_text(
                '"""Empty implementation — the minimal suite must not need it."""\n',
                encoding="utf-8",
            )

    # Drop the fixtures that require a database.
    conftest = tree / "tests" / "conftest.py"
    if conftest.is_file():
        conftest.write_text(_conftest_without_database(), encoding="utf-8")

    return tree


def _conftest_without_database() -> str:
    """Return the conftest with its database fixtures removed."""
    import re

    original = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    stripped = re.sub(
        DATABASE_SCHEMA_FIXTURE_PATTERN,
        "",
        original,
        flags=re.S,
    )
    stripped = re.sub(
        RESET_DATABASE_FIXTURE_PATTERN,
        "",
        stripped,
        flags=re.S,
    )
    return stripped


@pytest.fixture(scope="session", autouse=True)
def empty_implementation_fixture():
    """Fixture that provides an empty implementation context.

    This fixture is intentionally minimal — it does not set up any
    databases, services, or external dependencies. If this test fails,
    there is a genuine issue with the test configuration, not a defect
    in the project implementation.
    """
    # Yield control without setting up anything heavy
    return
    # Post-test: verify nothing unexpected happened
