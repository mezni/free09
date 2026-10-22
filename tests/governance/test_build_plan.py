"""Build plan test — the plan states every phase, its outcomes, and its gate.

Test ID: `test_build_plan_states_phases_and_exit_gates`
"""

import re

import pytest

from tests.governance.helpers import read, read_optional

pytestmark = pytest.mark.governance


class TestBuildPlan:
    """The build plan states what each phase delivers and how it closes."""

    def test_build_plan_states_phases_and_exit_gates(self):
        """Every phase section states its outcomes and its exit gate."""
        plan = read("docs/build-plan.md")

        sections = re.split(r"^###\s+", plan, flags=re.MULTILINE)[1:]
        assert sections, "The build plan states no phases."

        for section in sections:
            title = section.splitlines()[0].strip()
            assert "**Outcomes**" in section, f"Phase '{title}' states no outcomes."
            assert "**Exit gate**" in section, f"Phase '{title}' states no exit gate."

            gate = section.split("**Exit gate**", 1)[1]
            conditions = [
                line.strip()
                for line in gate.splitlines()
                if line.strip().startswith("- ")
            ]
            assert conditions, f"Phase '{title}' states no exit-gate condition."

    def test_phase_zero_has_recorded_evidence(self):
        """Phase 0 is stated, and its exit gate has an evidence document."""
        plan = read("docs/build-plan.md")
        assert "### Phase 0" in plan, "The build plan states no Phase 0."

        evidence = read_optional("docs/quality/phase-0-exit-gate.md")
        assert evidence, "Phase 0 has no recorded exit-gate evidence document."
