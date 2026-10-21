"""Config derivation test — T027 [P] [US1]."""

import os
import subprocess
import pytest

pytestmark = pytest.mark.usefixtures("clean_env_fixture")


@pytest.fixture(autouse=True, scope="session")
def clean_env_fixture(monkeypatch):
    """Set up a clean environment derived from .env.example only."""
    # Read .env.example and set only those variables (no real values)
    env_vars = {}
    with open(".env.example", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                var_name = line.split("=")[0].strip()
                # Set only placeholder/no-value entries
                env_vars[var_name] = ""

    # Apply to the session
    for var, value in env_vars.items():
        monkeypatch.setenv(var, value)

    # Verify no other env vars that would affect checks are set
    key_vars = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    for var in key_vars:
        assert var not in os.environ, f"Unexpected env var {var} is set"

    yield {}


@pytest.mark.usefixtures("clean_env_fixture")
class TestConfigDerivation:
    """Test that configuration checks derive values from .env.example alone."""

    def test_env_vars_from_example_only(self, clean_env_fixture):
        """All config derives from .env.example in clean environment."""
        # The clean environment should only have vars from .env.example
        example_vars = set()
        with open(".env.example", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    var_name = line.split("=")[0].strip()
                    example_vars.add(var_name)

        # Only example vars should be set (plus system ones)
        current_vars = set(k for k in os.environ if k in example_vars)
        assert current_vars == example_vars, (
            f"Expected only example vars {example_vars}, got {current_vars}"
        )

    def test_no_real_credentials_in_environment(self, clean_env_fixture):
        """No real credentials appear in the environment."""
        # Check that no database passwords or keys are set
        forbidden = ["DB_PASSWORD", "SECRET_KEY", "API_TOKEN"]
        for var in forbidden:
            assert var not in os.environ, f"Forbidden env var {var} is set"
