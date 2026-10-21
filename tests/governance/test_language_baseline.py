"""Language baseline test — T063 [P] [US1]."""


@pytest.mark.usefixtures("clone_dir_fixture")
class TestLanguageBaseline:
    """Test that language baseline is unchanged."""

    def test_python_version_matches(self):
        """Python 3.13 is the baseline version."""
        import sys
        assert sys.version_info >= (3, 13)

    def test_ruff_version(self):
        """Ruff is installed and operational."""
        import ruff
        assert ruff.__version__ is not None
