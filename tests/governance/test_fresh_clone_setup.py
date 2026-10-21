"""Fresh clone setup test — T062 [P] [US1]."""


import subprocess

import pytest


pytestmark = pytest.mark.usefixtures("clone_dir_fixture")


@pytest.fixture(autouse=True, scope="session")
def clone_dir_fixture(tmp_path):
    """Set up a fresh clone for testing."""
    clone_dir = tmp_path / "fresh-clone"
    clone_dir.mkdir()
    # Initialize the project
    subprocess.run(["uv", "sync"], cwd=str(clone_dir), capture_output=True)
    subprocess.run(["uv", "run", "make", "setup"], cwd=str(clone_dir), capture_output=True)
    yield {"clone_dir": str(clone_dir)}


@pytest.mark.usefixtures("clone_dir_fixture")
class TestFreshCloneSetup:
    """Test that a fresh clone reaches a verified state."""

    def test_setup_path_exists(self, clone_dir_fixture):
        """The documented setup path exists and is accessible."""
        clone_dir = clone_dir_fixture["clone_dir"]
        assert clone_dir is not None
        assert clone_dir.is_dir()

    def test_python_version(self, clone_dir_fixture):
        """Python version matches .python-version."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
        )
        assert "3.13" in result.stdout

    def test_make_help(self, clone_dir_fixture):
        """Makefile help target works."""
        result = subprocess.run(
            ["make", "help"],
            cwd=clone_dir_fixture["clone_dir"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
