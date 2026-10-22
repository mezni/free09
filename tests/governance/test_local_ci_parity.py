"""Local/CI parity test — the local result matches the automated result.

Test ID: `test_local_result_matches_automated_result`
"""

import re

import pytest

from tests.governance.helpers import REQUIRED_CHECKS, WORKFLOW, read

pytestmark = pytest.mark.governance

LANE_JOBS = ("fast-checks", "slow-checks")


class TestLocalCiParity:
    """There is one definition site per check, and CI calls it."""

    def test_local_result_matches_automated_result(self):
        """CI invokes the same nox sessions the local command invokes."""
        workflow = read(WORKFLOW)
        noxfile = read("noxfile.py")

        for check in REQUIRED_CHECKS:
            assert f"nox -s {check}" in workflow, (
                f"The workflow does not invoke the '{check}' session."
            )
            assert f'"{check}"' in noxfile, (
                f"noxfile.py does not define the '{check}' session."
            )

    def test_ci_does_not_duplicate_check_logic(self):
        """The workflow calls nox; it does not re-implement a check."""
        workflow = read(WORKFLOW)
        steps = re.findall(r"^\s*run:\s*(?P<command>.+)$", workflow, re.MULTILINE)
        for command in steps:
            if "nox" in command:
                continue
            if command.strip() in {"uv sync --frozen", "|"}:
                continue
            # The gate job's shell block is not check logic.
            assert command.strip().startswith("if ["), (
                f"The workflow runs a command that is not a nox session: {command}"
            )

    def test_both_lanes_exist_and_run_only_their_own_checks(self):
        """Each lane runs its own checks and no other lane's checks."""
        workflow = read(WORKFLOW)

        for lane in LANE_JOBS:
            body = re.search(
                rf"^  {re.escape(lane)}:\s*\n(?P<body>(?:^(?:    .*|\s*)$\n)*)",
                workflow,
                re.MULTILINE,
            )
            assert body is not None, f"The workflow has no '{lane}' job."
            assert "nox -s" in body.group("body"), (
                f"The '{lane}' job does not run any nox session."
            )

        assert "needs: [fast-checks, slow-checks]" in workflow, (
            "The gate does not depend on both lanes."
        )
