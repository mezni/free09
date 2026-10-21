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
