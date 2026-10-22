"""Secret history test — the version-controlled history holds no secret material.

Test ID: `test_no_secret_material_in_full_history`
"""

import shutil
import subprocess
import sys

import pytest

from tests.governance.helpers import REPO_ROOT

pytestmark = pytest.mark.governance

# The probe credential is assembled at run time so that no tracked file
# holds a literal that looks like a credential.
SECRET = "AKIA" + "YYYYYYYYYYYYYYYY"


class TestSecretScanHistory:
    """The scanner covers the history, not only the working tree."""

    def test_no_secret_material_in_full_history(self, tmp_path):
        """A secret that was removed from the tree is still found in the history."""
        repo = tmp_path / "probe"
        (repo / "ci").mkdir(parents=True)
        shutil.copy(REPO_ROOT / "ci" / "secret_scan.py", repo / "ci" / "secret_scan.py")

        (repo / "leaked.txt").write_text(f'AWS_KEY = "{SECRET}"\n', encoding="utf-8")

        for command in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "probe@example.invalid"],
            ["git", "config", "user.name", "Probe"],
            ["git", "add", "-A"],
            ["git", "commit", "-q", "-m", "add the leak"],
        ):
            subprocess.run(command, cwd=repo, check=True, capture_output=True)

        # Remove the file from the working tree and commit the removal. The
        # credential survives in the earlier commit.
        (repo / "leaked.txt").unlink()
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "remove the leak"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [sys.executable, "ci/secret_scan.py"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 1, (
            "The scanner did not find the secret that only exists in the "
            f"history (exit {result.returncode})."
        )
        output = result.stdout + result.stderr
        assert SECRET not in output, "The scanner printed the credential value."

    def test_this_repository_history_is_clean(self):
        """This repository's own history holds no secret material."""
        result = subprocess.run(
            [sys.executable, "ci/secret_scan.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            f"The repository's own history holds secret material:\n{result.stdout}"
        )
