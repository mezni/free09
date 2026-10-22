"""Local verification test — the documented command runs every required check.

Test ID: `test_local_verification_command_runs_all_required_checks`
"""

import re

import pytest

from tests.governance.helpers import (
    REQUIRED_CHECKS,
    contract_check_table,
    read,
)

pytestmark = pytest.mark.governance

SESSION = re.compile(
    r"^@nox\.session\((?P<args>[^)]*)\)\s*\n(?:[^\n]*\n)?def\s+(?P<func>\w+)\s*\(",
    re.MULTILINE,
)
SESSION_NAME = re.compile(r"""name=["'](?P<name>[^"']+)["']""")


def _nox_sessions() -> set[str]:
    """Return the nox session names the noxfile declares."""
    content = read("noxfile.py")
    sessions: set[str] = set()
    for match in SESSION.finditer(content):
        name = SESSION_NAME.search(match.group("args"))
        sessions.add(name.group("name") if name else match.group("func"))
    return sessions


class TestLocalVerification:
    """The local command and the contract agree on the required-check set."""

    def test_local_verification_command_runs_all_required_checks(self):
        """Every required check is a nox session the documented command runs."""
        sessions = _nox_sessions()
        missing = [check for check in REQUIRED_CHECKS if check not in sessions]
        assert not missing, (
            f"noxfile.py does not define these required-check sessions: {missing}"
        )

        contract_ids = [row["ID"].strip().strip("`") for row in contract_check_table()]
        assert contract_ids == REQUIRED_CHECKS, (
            "The verification contract's check table is not the nine required "
            f"checks in order: {contract_ids}"
        )

    def test_default_session_selection_is_the_required_set(self):
        """Running nox with no selection runs exactly the required checks."""
        content = read("noxfile.py")
        selection = re.search(
            r"nox\.options\.sessions\s*=\s*(?P<value>[A-Za-z_]+)", content
        )
        assert selection is not None, "noxfile.py does not set the default sessions."

        declared = re.search(r"REQUIRED_CHECKS\s*=\s*\[(?P<body>[^\]]*)\]", content)
        assert declared is not None, "noxfile.py does not declare REQUIRED_CHECKS."
        listed = re.findall(r"\"([^\"]+)\"", declared.group("body"))

        assert selection.group("value") == "REQUIRED_CHECKS", (
            "noxfile.py does not select the required checks by default."
        )
        assert listed == REQUIRED_CHECKS, (
            f"The noxfile's required checks are {listed}, not {REQUIRED_CHECKS}."
        )

    def test_makefile_exposes_the_documented_commands(self):
        """The Makefile exposes the verification command and the check targets."""
        makefile = read("Makefile")
        assert "nox" in makefile, "The Makefile does not delegate to nox."
        assert re.search(r"^verify:", makefile, re.MULTILINE), (
            "The Makefile has no 'verify' target."
        )
        for target in (
            "test",
            "lint",
            "format",
            "typecheck",
            "secret-scan",
            "dependency-audit",
            "governance",
            "file-coverage",
            "lockfile",
        ):
            assert re.search(rf"^{re.escape(target)}:", makefile, re.MULTILINE), (
                f"The Makefile has no '{target}' target."
            )
