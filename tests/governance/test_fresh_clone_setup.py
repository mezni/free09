"""Fresh clone setup test — T062 [P] [US1]."""

import subprocess

import pytest

pytestmark = pytest.mark.usefixtures("clone_dir_fixture")


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
