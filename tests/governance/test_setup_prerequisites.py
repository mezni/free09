"""Setup prerequisites test — T064 [P] [US1]."""

import pathlib
import subprocess
import sys

import pytest


@pytest.mark.usefixtures("clone_dir_fixture")
class TestSetupPrerequisites:
    """Test that setup prerequisites are met."""

    def test_uv_installed(self):
        """uv package manager is installed."""
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_nox_installed(self, tool_bin_fixture):
        """nox is installed."""
        nox_bin = tool_bin_fixture("nox")
        assert nox_bin is not None, "nox is not installed in the active environment"

        result = subprocess.run(
            [nox_bin, "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_make_present(self):
        """Makefile is present."""
        assert pathlib.Path("Makefile").is_file()

    def test_python_version(self):
        """Python 3.13 is the required version."""
        assert sys.version_info >= (3, 13)

    def test_setup_names_missing_prerequisite(self):
        """The prerequisite check names what is missing and what is required.

        The check runs with an empty `PATH`, so every tool it looks for is
        absent. The failure it reports must name each missing tool, say what
        is needed, and exit with the "could not run" code.
        """
        result = subprocess.run(
            [sys.executable, "ci/check_prerequisites.py"],
            capture_output=True,
            text=True,
            env={"PATH": "", "HOME": str(pathlib.Path.home())},
            check=False,
        )

        assert result.returncode == 2, (
            "A missing prerequisite must exit with the 'could not run' code 2, "
            f"not {result.returncode}."
        )

        output = result.stdout
        for prerequisite in (
            "UV workspace manager",
            "Docker daemon",
            "Git version control",
            "Make build tool",
            "Python interpreter",
        ):
            assert prerequisite in output, (
                f"The prerequisite check does not name the missing {prerequisite}."
            )

        assert "Prerequisite check FAILED" in output, (
            "The prerequisite check does not report its verdict."
        )
