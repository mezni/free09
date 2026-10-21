"""Example config test — T026 [P] [US1]."""

import pytest

pytestmark = pytest.mark.usefixtures("example_config_fixture")


@pytest.fixture(autouse=True, scope="session")
def example_config_fixture():
    """Provide the example configuration and verify its properties."""
    # Read the .env.example and verify its properties
    with open(".env.example", "r") as f:
        content = f.read()

    variables = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            var_name = line.split("=")[0].strip()
            var_desc = line.split("=", 1)[1].strip()
            variables.append((var_name, var_desc))

    # Verify no usable credentials/keys/connection strings are present
    for var_name, var_desc in variables:
        lower_desc = var_desc.lower()
        forbidden_keywords = [
            "secret", "credential", "key", "password",
            "connection string", "connection_string",
        ]
        for kw in forbidden_keywords:
            assert kw not in lower_desc, (
                f"Variable {var_name} has forbidden keyword '{kw}' in description: {var_desc}"
            )

    # Verify every required variable has a purpose listed
    for var_name, var_desc in variables:
        # Each variable should have a purpose (required/optional status)
        assert ":" in var_desc or "required" in var_desc.lower() or "optional" in var_desc.lower(), (
            f"Variable {var_name} missing purpose/status in description: {var_desc}"
        )

    return {"variables": variables}


@pytest.mark.usefixtures("example_config_fixture")
class TestExampleConfig:
    """Test that example configuration is properly configured."""

    def test_no_secret_material(self, example_config_fixture):
        """No usable credential, key, or connection string in descriptions."""
        variables = example_config_fixture["variables"]
        for var_name, var_desc in variables:
            lower = var_desc.lower()
            assert "secret" not in lower, f"Variable {var_name} references a secret"
            assert "key" not in lower, f"Variable {var_name} references a key"
            assert "password" not in lower, f"Variable {var_name} references a password"

    def test_purpose_listed(self, example_config_fixture):
        """Every variable has its purpose (required/optional) listed."""
        variables = example_config_fixture["variables"]
        for var_name, var_desc in variables:
            assert (
                ":" in var_desc or "required" in var_desc.lower() or "optional" in var_desc.lower()
            ), f"Variable {var_name} missing purpose in description"
