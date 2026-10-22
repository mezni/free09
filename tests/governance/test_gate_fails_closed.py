"""Gate test — a failing or inconclusive check blocks the merge.

Test ID: `test_failed_or_inconclusive_check_blocks_merge`
"""

import json
import re

import pytest

from tests.governance.helpers import WORKFLOW, read, read_optional

pytestmark = pytest.mark.governance

GATE_JOB = "required-checks"
LANE_JOBS = ("fast-checks", "slow-checks")


def _job_body(workflow: str, job_id: str) -> str:
    """Return the body of a job in the workflow."""
    match = re.search(
        rf"^  {re.escape(job_id)}:\s*\n(?P<body>(?:^(?:    .*|\s*)$\n)*)",
        workflow,
        re.MULTILINE,
    )
    return match.group("body") if match else ""


class TestGateFailsClosed:
    """The merge gate fails closed."""

    def test_failed_or_inconclusive_check_blocks_merge(self):
        """A non-success lane result fails the gate and blocks the merge."""
        workflow = read(WORKFLOW)
        gate = _job_body(workflow, GATE_JOB)

        assert gate, f"The workflow does not define the '{GATE_JOB}' job."
        assert "if: always()" in gate, (
            "The gate does not run under 'if: always()'; a skipped lane would "
            "read as a pass."
        )
        assert "continue-on-error" not in gate, (
            "The gate uses 'continue-on-error'; a failing lane would stop "
            "blocking the merge."
        )

        needs = re.search(r"^\s*needs:\s*\[(?P<jobs>[^\]]*)\]", gate, re.MULTILINE)
        assert needs is not None, "The gate declares no 'needs:' list."
        declared = {item.strip() for item in needs.group("jobs").split(",")}
        assert set(LANE_JOBS) <= declared, (
            f"The gate depends on {sorted(declared)}, not on both lanes."
        )

        for lane in LANE_JOBS:
            assert f"needs.{lane}.result" in gate, (
                f"The gate does not inspect the '{lane}' result."
            )

    def test_ruleset_requires_the_gate_context(self):
        """The branch ruleset makes the gate job a required status check."""
        ruleset = read_optional(".github/rulesets/main-required-checks.json")
        assert ruleset, "The repository has no branch ruleset."

        parsed = json.loads(ruleset)
        contexts = [
            check.get("context")
            for rule in parsed.get("rules", [])
            if rule.get("type") == "required_status_checks"
            for check in rule.get("parameters", {}).get("required_status_checks", [])
        ]
        assert GATE_JOB in contexts, (
            f"The ruleset requires {contexts}, not the '{GATE_JOB}' gate."
        )

    def test_exit_codes_one_and_two_both_fail(self):
        """The contract states that both a failure and an inconclusive check fail."""
        contract = read("specs/001-project-setup/contracts/verification-contract.md")
        assert "**Both `1` and `2` are failures at the gate.**" in contract, (
            "The verification contract does not state that exit codes 1 and 2 "
            "both fail the gate."
        )
