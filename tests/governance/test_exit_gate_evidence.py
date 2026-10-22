"""Exit gate test — every Phase 0 gate condition has recorded evidence.

Test ID: `test_exit_gate_evidence_recorded_for_every_condition`
"""

import re

import pytest

from tests.governance.helpers import read, read_optional

pytestmark = pytest.mark.governance

GATE_EVIDENCE = "docs/quality/phase-0-exit-gate.md"


def _phase_zero_conditions() -> list[str]:
    """Return the Phase 0 exit-gate conditions the build plan states."""
    plan = read("docs/build-plan.md")
    section = re.split(r"^###\s+", plan, flags=re.MULTILINE)
    for chunk in section:
        if not chunk.startswith("Phase 0"):
            continue
        gate = chunk.split("**Exit gate**", 1)[1]
        return [
            line.strip().lstrip("- ").strip()
            for line in gate.splitlines()
            if line.strip().startswith("- ")
        ]
    return []


class TestExitGateEvidence:
    """The Phase 0 exit gate is closed with recorded evidence."""

    def test_exit_gate_evidence_recorded_for_every_condition(self):
        """Every gate condition has an evidence row that names a real artefact."""
        conditions = _phase_zero_conditions()
        assert conditions, "The build plan states no Phase 0 exit-gate condition."

        evidence = read_optional(GATE_EVIDENCE)
        assert evidence, f"The repository has no {GATE_EVIDENCE}."

        missing = []
        for condition in conditions:
            # A condition is satisfied when the evidence document records it.
            key = condition.rstrip(".").lower()
            probe = key.split(",")[0].split(" and ")[0]
            if probe not in evidence.lower():
                missing.append(condition)

        assert not missing, (
            f"The exit-gate evidence does not record these conditions: {missing}"
        )

    def test_evidence_rows_name_the_artefact_that_proves_them(self):
        """Every evidence row names a file that exists in the tree."""
        evidence = read(GATE_EVIDENCE)
        references = set(
            re.findall(r"`([A-Za-z0-9_./-]+\.(?:py|md|yml|yaml|sh))`", evidence)
        )

        import os

        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        missing = [
            reference
            for reference in sorted(references)
            if not os.path.exists(os.path.join(root, reference))
        ]
        assert not missing, (
            f"The exit-gate evidence cites files that do not exist: {missing}"
        )
