"""Decision record test — an accepted ADR follows the template.

Test ID: `test_completed_decision_record_matches_template`
"""

import re
from pathlib import Path

import pytest

from tests.governance.helpers import REPO_ROOT

pytestmark = pytest.mark.governance

REQUIRED_SECTIONS = (
    "## Context",
    "## Decision drivers",
    "## Options considered",
    "## Decision",
    "## Consequences",
    "## Revisit triggers",
)

STATUS = re.compile(r"^- Status:\s*(?P<status>.+)$", re.MULTILINE)


def _adrs() -> list[Path]:
    """Return the decision records in the repository."""
    adr_dir = REPO_ROOT / "docs" / "adr"
    if not adr_dir.is_dir():
        return []
    return sorted(adr_dir.glob("ADR-*.md"))


class TestDecisionRecordFormat:
    """Every accepted decision record is complete."""

    def test_completed_decision_record_matches_template(self):
        """Each accepted record states context, options, decision, and consequences."""
        adrs = _adrs()
        assert adrs, "The repository holds no decision records."

        accepted = []
        for adr in adrs:
            content = adr.read_text(encoding="utf-8")
            status = STATUS.search(content)
            assert status is not None, f"{adr.name} states no status."
            if status.group("status").strip() == "Accepted":
                accepted.append(adr)

        assert accepted, "No decision record is accepted."

        for adr in accepted:
            content = adr.read_text(encoding="utf-8")
            missing = [
                section for section in REQUIRED_SECTIONS if section not in content
            ]
            assert not missing, f"{adr.name} is missing the sections {missing}."

            options = content.split("## Options considered", 1)[1]
            options = options.split("##", 1)[0]
            assert len(re.findall(r"^\d+\.\s", options, re.MULTILINE)) >= 2, (
                f"{adr.name} does not consider at least two options."
            )

            consequences = content.split("## Consequences", 1)[1]
            has_positive = "Positive:" in consequences
            has_negative = "Negative:" in consequences
            assert has_positive, f"{adr.name} does not state the positive consequences."
            assert has_negative, f"{adr.name} does not state the negative consequences."

    def test_record_numbers_are_unique_and_sequential(self):
        """Decision record numbers are unique and sequential."""
        numbers = []
        for adr in _adrs():
            match = re.match(r"ADR-(\d{4})-", adr.name)
            assert match is not None, f"{adr.name} does not follow the naming rule."
            numbers.append(int(match.group(1)))

        assert len(numbers) == len(set(numbers)), "Decision record numbers repeat."
        expected = list(range(1, len(numbers) + 1))
        assert sorted(numbers) == expected, (
            f"The decision record numbers are not sequential: {sorted(numbers)}"
        )
