"""Configuration agreement test — the contract, the example, and the code agree.

Test ID: `test_configuration_contract_and_code_agree`
"""

import re

import pytest

from tests.governance.helpers import REPO_ROOT, markdown_tables, read

pytestmark = pytest.mark.governance

CONFIG_CONTRACT = "specs/001-project-setup/contracts/configuration-contract.md"
ENV_EXAMPLE = ".env.example"

# The variable the implementation reads.
IMPLEMENTED_VARIABLES = (
    "TELECO_ENV",
    "TELECO_SERVICE_NAME",
    "TELECO_SERVICE_ROLE",
    "TELECO_DB_URL",
)


def _example_variables() -> dict[str, str]:
    """Return the variables declared in `.env.example`."""
    content = read(ENV_EXAMPLE)
    variables: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, _, value = stripped.partition("=")
        variables[name.strip()] = value.strip()
    return variables


def _contract_variables() -> set[str]:
    """Return the variable names the configuration contract declares.

    The contract declares names in the `Name` column of its variable tables.
    A name that appears only in prose — a variable the contract mentions but
    does not declare — is not a declaration.
    """
    content = read(CONFIG_CONTRACT)
    declared: set[str] = set()

    for table in markdown_tables(content):
        header = [cell.strip() for cell in table[0]]
        if "Name" not in header:
            continue
        name_column = header.index("Name")
        for row in table[1:]:
            if len(row) <= name_column:
                continue
            candidate = row[name_column].strip().strip("`")
            if re.fullmatch(r"[A-Z][A-Z0-9_]+", candidate):
                declared.add(candidate)

    return declared


class TestConfigAgreement:
    """The configuration contract, `.env.example`, and the code agree."""

    def test_configuration_contract_and_code_agree(self):
        """Every variable the code reads is declared by the contract."""
        contract = _contract_variables()
        assert contract, (
            f"{CONFIG_CONTRACT} declares no variable; it cannot agree with anything."
        )

        example = set(_example_variables())
        missing = sorted(contract - example)
        assert not missing, (
            f"{CONFIG_CONTRACT} declares variables that {ENV_EXAMPLE} does "
            f"not: {missing}"
        )

        implemented = []
        for path in sorted(REPO_ROOT.glob("src/**/*.py")):
            content = path.read_text(encoding="utf-8")
            implemented.extend(re.findall(r'"(TELECO_[A-Z0-9_]+)"', content))

        undeclared = sorted(set(implemented) - contract)
        assert not undeclared, (
            "The code reads variables the configuration contract does not "
            f"declare: {undeclared}"
        )

    def test_the_contract_declares_the_reserved_database_variables(self):
        """The contract reserves the per-service database variables."""
        contract = _contract_variables()
        for name in ("TELECO_DB_URL", "TELECO_DB_HOST", "TELECO_DB_PORT"):
            assert name in contract, f"{CONFIG_CONTRACT} does not reserve {name}."

    def test_the_example_declares_every_implemented_variable(self):
        """`.env.example` carries every variable the implementation reads."""
        example = set(_example_variables())
        for name in IMPLEMENTED_VARIABLES:
            assert name in example, f"{ENV_EXAMPLE} does not declare {name}."

    def test_the_example_is_the_single_source_of_the_variable_list(self):
        """The variable list in the example and the contract are the same set."""
        example = set(_example_variables())
        contract = _contract_variables()
        extra = sorted(example - contract)
        assert not extra, (
            f"{ENV_EXAMPLE} declares variables the contract does not: {extra}"
        )

    def test_the_environment_settings_are_documented_where_they_are_read(self):
        """Every implemented variable has a comment in `.env.example`."""
        content = read(ENV_EXAMPLE)
        documented = set(
            re.findall(
                r"^#\s*([A-Z0-9_]+):\s*(required|optional)", content, re.MULTILINE
            )
        )
        documented = {name for name, _ in documented}
        for name in _example_variables():
            assert name in documented, (
                f"{ENV_EXAMPLE} declares {name} with no comment naming its "
                "required status."
            )
