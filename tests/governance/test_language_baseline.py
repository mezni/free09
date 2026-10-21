"""Language baseline test — T063 [P] [US1]."""

import subprocess
import sys

import pytest


@pytest.mark.usefixtures("clone_dir_fixture")
class TestLanguageBaseline:
    """Test that language baseline is unchanged."""

    def test_python_version_matches(self):
        """Python 3.13 is the baseline version."""
        assert sys.version_info >= (3, 13)

    def test_ruff_version(self, tool_bin_fixture):
        """Ruff is installed and operational."""
        ruff_bin = tool_bin_fixture("ruff")
        assert ruff_bin is not None, "ruff is not installed in the active environment"

        result = subprocess.run(
            [ruff_bin, "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "ruff" in result.stdout.lower()
