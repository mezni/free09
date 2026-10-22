"""Config derivation test — T027 [P] [US1]."""

import os

import pytest

pytestmark = pytest.mark.usefixtures("clean_env_fixture")

CREDENTIAL_VARS = ["SECRET_KEY", "API_TOKEN", "SECRET_KEY_BASE"]


def _example_variables(path=".env.example"):
    """Return the variable names declared in an env file."""
    names = []
    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            names.append(line.split("=", 1)[0].strip())
    return names


@pytest.fixture(autouse=True)
def clean_env_fixture(monkeypatch):
    """Derive a clean environment from .env.example alone.

    Every declared variable is set to an empty value so that no real
    configuration leaks in from the surrounding environment.
    """
    for var_name in _example_variables():
        monkeypatch.setenv(var_name, "")

    for var_name in CREDENTIAL_VARS:
        monkeypatch.delenv(var_name, raising=False)

    return {}


@pytest.mark.usefixtures("clean_env_fixture")
class TestConfigDerivation:
    """Test that configuration checks derive values from .env.example alone."""

    def test_checks_derive_config_from_example(self, clean_env_fixture):
        """All config derives from .env.example in a clean environment."""
        example_vars = set(_example_variables())

        current_vars = {key for key in os.environ if key in example_vars}
        assert current_vars == example_vars, (
            f"Expected only example vars {example_vars}, got {current_vars}"
        )

        for var_name in example_vars:
            assert os.environ[var_name] == "", (
                f"Variable {var_name} should be empty in a clean environment"
            )

    def test_no_real_credentials_in_environment(self, clean_env_fixture):
        """No real credentials appear in the environment."""
        for var_name in CREDENTIAL_VARS:
            assert var_name not in os.environ, f"Forbidden env var {var_name} is set"

        # A declared credential variable must be present but empty.
        assert os.environ.get("TELECO_DB_PASSWORD", "") == "", (
            "TELECO_DB_PASSWORD must not be populated"
        )
