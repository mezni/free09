"""CI acceptance/rejection test — T035 [P] [US2].

Test ID: `test_continuous_verification_accepts_and_rejects_changes`
"""

import re
import subprocess
import sys

import pytest

from tests.governance.helpers import REPO_ROOT, read

pytestmark = pytest.mark.usefixtures("ci_session_fixture")

WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"

# A representative, non-recursive subset: running the whole suite from inside
# the suite would re-enter this fixture and never terminate.
REPRESENTATIVE_SUITE = "tests/governance/test_language_baseline.py"


def _run(command: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


@pytest.fixture(autouse=True, scope="session")
def ci_session_fixture():
    """Fixture that runs CI checks and records outcomes."""
    # Test 1: Formatting check (ruff format)
    result_format = _run(
        [sys.executable, "-m", "ruff", "format", "--check", "."], timeout=300
    )

    # Test 2: Lint check (ruff check)
    result_lint = _run([sys.executable, "-m", "ruff", "check", "."], timeout=300)

    # Test 3: Test check (representative suite)
    result_test = _run(
        [sys.executable, "-m", "pytest", REPRESENTATIVE_SUITE, "-q"], timeout=300
    )

    return {
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
        """The formatting check accepts the tree as it stands."""
        outcome = ci_session_fixture["format_exit"]
        assert outcome == 0, (
            "The tree is not formatted; the formatting check must accept it:\n"
            f"{ci_session_fixture['format_stdout']}"
        )

    def test_lint_check_outcome(self, ci_session_fixture):
        """The lint check accepts the tree as it stands."""
        outcome = ci_session_fixture["lint_exit"]
        assert outcome == 0, (
            "The tree does not pass lint; the lint check must accept it:\n"
            f"{ci_session_fixture['lint_stdout']}"
        )

    def test_test_check_outcome(self, ci_session_fixture):
        """The test check accepts the tree as it stands."""
        outcome = ci_session_fixture["test_exit"]
        assert outcome == 0, (
            "The tree does not pass the test check; it must accept it:\n"
            f"{ci_session_fixture['test_stdout']}"
        )

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
            assert code in valid_codes, (
                f"CI check '{name}' has invalid exit code: {code}"
            )

    def test_continuous_verification_accepts_and_rejects_changes(self):
        """Continuous verification runs on every change and rejects a failure.

        The workflow must trigger on every push and every pull request, it
        must not narrow itself to a branch or a path, and the gate job must
        fail when a lane does not succeed.
        """
        content = read(".github/workflows/ci.yml")

        triggers = re.search(r"^on:\n((?:\s+.*\n)+)", content, re.MULTILINE)
        assert triggers, "The workflow declares no trigger."
        trigger_block = triggers.group(1)

        assert re.search(r"^\s+push:", trigger_block, re.MULTILINE), (
            "The workflow does not run on a push; continuous verification must "
            "run on every change."
        )
        assert re.search(r"^\s+pull_request:", trigger_block, re.MULTILINE), (
            "The workflow does not run on a pull request."
        )

        assert "branches:" not in trigger_block, (
            "The workflow narrows itself to a branch; continuous verification "
            "must run on every change."
        )
        assert "paths:" not in trigger_block, (
            "The workflow narrows itself to a path; continuous verification "
            "must run on every change."
        )

        gate = re.search(
            r"^  required-checks:\n((?:\s+.*\n)+?)(?=^  \S|\Z)",
            content,
            re.MULTILINE,
        )
        assert gate, "The workflow declares no required-checks gate job."
        gate_block = gate.group(1)

        assert "if: always()" in gate_block, (
            "The gate does not run when a lane fails; it must run under "
            "`if: always()` so that a failure is reported as a failure."
        )
        assert "continue-on-error" not in gate_block, (
            "The gate continues on error; it must fail the merge."
        )
        assert re.search(r"needs:\s*\[.*fast-checks.*\]", gate_block), (
            "The gate does not depend on the fast lane."
        )
        assert re.search(r"needs:\s*\[.*slow-checks.*\]", gate_block), (
            "The gate does not depend on the slow lane."
        )
        for lane in ("fast-checks", "slow-checks"):
            assert re.search(rf"needs\.{lane}\.result[^\n]*success", gate_block), (
                f"The gate does not require the {lane} lane to succeed; a "
                "failed or inconclusive lane must fail the merge."
            )
