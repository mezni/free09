"""Example config test — T026 [P] [US1]."""

import pytest

pytestmark = pytest.mark.usefixtures("example_config_fixture")

PLACEHOLDER_PREFIXES = ("placeholder", "changeme", "change_me", "example", "dummy")
REQUIRED_STATUSES = ("required", "optional")


def _parse_env_example(path=".env.example"):
    """Parse an env file into (variable, value, purpose) triples.

    A purpose is the text of the comment line that immediately precedes the
    assignment, which names the variable and states its required status.
    """
    entries = []
    pending_comment = ""

    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("#"):
                pending_comment = line.lstrip("#").strip()
                continue

            if "=" not in line:
                pending_comment = ""
                continue

            var_name, _, value = line.partition("=")
            entries.append((var_name.strip(), value.strip(), pending_comment))
            pending_comment = ""

    return entries


@pytest.fixture(autouse=True)
def example_config_fixture():
    """Provide the example configuration and verify its properties."""
    variables = _parse_env_example()

    # Verify no usable credentials/keys/connection strings are present. A
    # value that is explicitly a placeholder is by definition not usable.
    for var_name, value, _purpose in variables:
        if not value:
            continue
        if value.lower().startswith(PLACEHOLDER_PREFIXES):
            continue
        lower_value = value.lower()
        forbidden_keywords = [
            "secret",
            "credential",
            "password",
            "connection string",
            "connection_string",
        ]
        for keyword in forbidden_keywords:
            assert keyword not in lower_value, (
                f"Variable {var_name} contains forbidden keyword "
                f"'{keyword}' in value: {value}"
            )

    return {"variables": variables}


@pytest.mark.usefixtures("example_config_fixture")
class TestExampleConfig:
    """Test that example configuration is properly configured."""

    def test_no_secret_material(self, example_config_fixture):
        """No usable credential, key, or connection string in values."""
        for var_name, value, _purpose in example_config_fixture["variables"]:
            if not value or value.lower().startswith(PLACEHOLDER_PREFIXES):
                continue
            lower = value.lower()
            assert "secret" not in lower, f"Variable {var_name} references a secret"
            assert "key" not in lower, f"Variable {var_name} references a key"
            assert "password" not in lower, f"Variable {var_name} references a password"

    def test_purpose_listed(self, example_config_fixture):
        """Every variable has its purpose (required/optional) listed."""
        for var_name, _value, purpose in example_config_fixture["variables"]:
            assert purpose, f"Variable {var_name} has no purpose comment"
            assert var_name in purpose, (
                f"Purpose comment for {var_name} does not name the variable: {purpose}"
            )
            assert any(status in purpose.lower() for status in REQUIRED_STATUSES), (
                f"Variable {var_name} missing required/optional status: {purpose}"
            )
