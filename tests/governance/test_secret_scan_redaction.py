"""Secret scan test — a credential is rejected and never printed.

Test ID: `test_secret_detection_blocks_and_redacts`
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.governance.helpers import REPO_ROOT

pytestmark = pytest.mark.governance

# The probe credential is assembled at run time so that no tracked file
# holds a literal that looks like a credential. The scanner still sees the
# full value in the probe repository it builds.
SECRET = "AKIA" + "ZZZZZZZZZZZZZZZZ"


def _scan_a_repo_with_a_secret(repo: Path) -> subprocess.CompletedProcess:
    """Build a repository containing the scanner and one secret, then scan it."""
    (repo / "ci").mkdir(parents=True)
    shutil.copy(REPO_ROOT / "ci" / "secret_scan.py", repo / "ci" / "secret_scan.py")

    (repo / "leaked.txt").write_text(f'AWS_KEY = "{SECRET}"\n', encoding="utf-8")

    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "probe@example.invalid"],
        ["git", "config", "user.name", "Probe"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "probe"],
    ):
        subprocess.run(command, cwd=repo, check=True, capture_output=True)

    return subprocess.run(
        [sys.executable, "ci/secret_scan.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


class TestSecretScanRedaction:
    """The scanner finds a credential, names it, and never prints it."""

    def test_secret_detection_blocks_and_redacts(self, tmp_path):
        """The scanner fails, names the file and the rule, and redacts the value."""
        result = _scan_a_repo_with_a_secret(tmp_path / "probe")

        assert result.returncode == 1, (
            f"The scanner did not reject the secret (exit {result.returncode}):\n"
            f"{result.stdout}"
        )

        output = result.stdout + result.stderr
        assert "leaked.txt" in output, "The scanner did not name the offending file."
        assert "aws-access-key-id" in output, (
            "The scanner did not name the violated rule."
        )
        assert SECRET not in output, (
            "The scanner printed the detected credential value; the output must "
            "be redacted."
        )
        assert "***REDACTED***" in output, (
            "The scanner did not mark the finding as redacted."
        )

    def test_scanner_reports_the_check_id_and_a_single_result_word(self, tmp_path):
        """The scanner's output follows the contract's output format."""
        result = _scan_a_repo_with_a_secret(tmp_path / "probe")

        first_line = result.stdout.splitlines()[0].strip()
        assert first_line == "FAIL", (
            f"The first output line is '{first_line}', not the single word FAIL."
        )
        assert result.stdout.splitlines()[1].strip() == "secret-scan", (
            "The scanner does not report its check ID."
        )
