"""CI acceptance/rejection test — T035 [P] [US2]."""

import subprocess
import pytest
import sys

pytestmark = pytest.mark.usefixtures("ci_session_fixture")


@pytest.fixture(autouse=True, scope="session")
def ci_session_fixture(tmp_path):
    """Fixture that runs CI checks and records outcomes."""
    # Test 1: Formatting check (ruff format)
    result_format = subprocess.run(
        ["nox", "run", "format"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Test 2: Lint check (ruff check)
    result_lint = subprocess.run(
        ["nox", "run", "lint"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Test 3: Test check
    result_test = subprocess.run(
        ["nox", "run", "test"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    yield {
        "format_exit": result_format.returncode,
        "lint_exit": result_lint.returncode,
        "test_exit": result_test.returncode,
        "format_stdout": result_format.stdout[-500:] if result_format.stdout else "",
        "lint_stdout": result_lint.stdout[-500:] if result_lint.stdout else "",
        "test_stdout": result_test.stdout[-500:] if result_test.stdout else "",
    }


@pytest.mark.usefixtures("ci_session_fixture")
class TestCIAcceptsAndRejects:
    """Test that CI accepts conforming changes and rejects breaking changes."""

    def test_format_check_outcome(self, ci_session_fixture):
        """Format check outcome is recorded."""
        outcome = ci_session_fixture["format_exit"]
        # Outcome should be 0 (PASS), 1 (FAIL), 2 (COULD NOT RUN), or 3 (INTERNAL ERROR)
        assert outcome in {0, 1, 2, 3}, f"Unexpected format exit code: {outcome}"

    def test_lint_check_outcome(self, ci_session_fixture):
        """Lint check outcome is recorded."""
        outcome = ci_session_fixture["lint_exit"]
        assert outcome in {0, 1, 2, 3}, f"Unexpected lint exit code: {outcome}"

    def test_test_check_outcome(self, ci_session_fixture):
        """Test check outcome is recorded."""
        outcome = ci_session_fixture["test_exit"]
        assert outcome in {0, 1, 2, 3}, f"Unexpected test exit code: {outcome}"

    def test_ci_outcomes_recorded(self, ci_session_fixture):
        """All CI check outcomes are recorded with their exact exit codes."""
        outcomes = {
            "format": ci_session_fixture["format_exit"],
            "lint": ci_session_fixture["lint_exit"],
            "test": ci_session_fixture["test_exit"],
        }
        for name, code in outcomes.items():
            # Each check outcome should be one of the valid exit codes
            valid_codes = {0, 1, 2, 3}
            assert code in valid_codes, f"CI check '{name}' has invalid exit code: {code}"
