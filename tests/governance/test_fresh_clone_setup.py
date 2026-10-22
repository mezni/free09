"""Fresh clone setup test — T062 [P] [US1].

Test ID: `test_fresh_clone_setup_reaches_verified_state`
"""

import subprocess
import sys
from pathlib import Path

import pytest

from tests.governance.helpers import REPO_ROOT

pytestmark = pytest.mark.usefixtures("clone_dir_fixture")

# The files a clone needs before it can be verified.
SETUP_ARTEFACTS = (
    "ci/setup.sh",
    "ci/check_prerequisites.py",
    ".env.example",
    "pyproject.toml",
    "uv.lock",
    "Makefile",
    "noxfile.py",
)

# The required checks the clone runs to prove it reached a verified state.
VERIFICATION_SCRIPTS = (
    "ci/check_spec_artifacts.py",
    "ci/check_file_coverage.py",
    "ci/check_dependencies.py",
    "ci/secret_scan.py",
)


@pytest.mark.usefixtures("clone_dir_fixture")
class TestFreshCloneSetup:
    """Test that a fresh clone reaches a verified state."""

    def test_setup_path_exists(self, clone_dir_fixture):
        """The documented setup path exists and is accessible."""
        clone_dir = clone_dir_fixture["clone_dir"]
        assert clone_dir is not None
        assert clone_dir.is_dir()

    def test_python_version(self):
        """Python version matches .python-version."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
        )
        assert "3.13" in result.stdout

    def test_make_help(self):
        """Makefile help target works."""
        result = subprocess.run(
            ["make", "help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "verification" in result.stdout or "test" in result.stdout

    def test_fresh_clone_setup_reaches_verified_state(self):
        """A clone reaches a verified state by following the setup path.

        The repository is cloned into a scratch directory, the documented
        setup path is run there, and the clone's own verification command is
        run. The clone must reach a verified state without reaching the
        network: the dependency sync resolves from the lockfile and the
        local package cache.
        """
        import tempfile

        with tempfile.TemporaryDirectory(prefix="fresh-clone-") as workspace:
            clone = Path(workspace) / "clone"

            cloned = subprocess.run(
                [
                    "git",
                    "clone",
                    "--quiet",
                    "--no-hardlinks",
                    str(REPO_ROOT),
                    str(clone),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=300,
            )
            assert cloned.returncode == 0, (
                f"The repository does not clone:\n{cloned.stderr}"
            )

            for artefact in SETUP_ARTEFACTS:
                assert (clone / artefact).exists(), (
                    f"A fresh clone does not carry {artefact}."
                )

            prerequisites = subprocess.run(
                [sys.executable, "ci/check_prerequisites.py"],
                cwd=clone,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            assert prerequisites.returncode == 0, (
                "The prerequisite check fails in a fresh clone:\n"
                f"{prerequisites.stdout}"
            )

            synced = subprocess.run(
                ["uv", "sync", "--frozen", "--offline", "--all-packages"],
                cwd=clone,
                capture_output=True,
                text=True,
                check=False,
                timeout=600,
            )
            assert synced.returncode == 0, (
                "The dependency sync fails in a fresh clone:\n"
                f"{synced.stdout}\n{synced.stderr}"
            )

            # The setup path's last step: the example configuration becomes
            # the local configuration.
            (clone / ".env").write_text(
                (clone / ".env.example").read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            # The clone's own verification: every required check script the
            # clone carries must pass there.
            for script in VERIFICATION_SCRIPTS:
                if not (clone / script).is_file():
                    continue
                verified = subprocess.run(
                    [sys.executable, script],
                    cwd=clone,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=300,
                )
                assert verified.returncode == 0, (
                    f"The clone does not reach a verified state; {script} "
                    f"failed:\n{verified.stdout[-4000:]}"
                )
