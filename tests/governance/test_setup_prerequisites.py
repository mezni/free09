"""Setup prerequisites test — T064 [P] [US1]."""


@pytest.mark.usefixtures("clone_dir_fixture")
class TestSetupPrerequisites:
    """Test that setup prerequisites are met."""

    def test_uv_installed(self):
        """uv package manager is installed."""
        result = __import__('subprocess').run(
            ['uv', '--version'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_nox_installed(self):
        """nox is installed."""
        result = __import__('subprocess').run(
            ['nox', '--version'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_make_present(self):
        """Makefile is present."""
        import pathlib
        assert pathlib.Path('Makefile').is_file()

    def test_python_version(self):
        """Python 3.13 is the required version."""
        import sys
        assert sys.version_info >= (3, 13)
