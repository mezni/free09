"""Open-questions test — every open question has an owner and a due phase.

Test ID: `test_open_questions_have_an_owner_and_a_due_phase`
"""

import re

import pytest

from tests.governance.helpers import read, read_optional

pytestmark = pytest.mark.governance

OPEN_QUESTIONS = "docs/risks/open-questions.md"

# A phase the repository names.
PHASES = tuple(f"Phase {number}" for number in range(0, 12))

# A due-phase value that names no phase.
UNSET_OWNERS = {"", "-", "—", "tbd", "n/a", "unassigned", "unknown"}


def _table_rows(section: str) -> list[list[str]]:
    """Return the table rows of a section as cell lists."""
    rows = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.fullmatch(r"\|[\s:|-]+\|", stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows


def _sections(content: str) -> dict[str, list[list[str]]]:
    """Return the table rows of each `##` section of a document."""
    result: dict[str, list[list[str]]] = {}
    name = ""
    for line in content.splitlines():
        if line.startswith("## "):
            name = line[3:].strip()
            result.setdefault(name, [])
            continue
        if name:
            result[name].extend(_table_rows(line))
    return result


class TestOpenQuestionsOwned:
    """No open question is unowned."""

    def test_open_questions_have_owner_and_due_phase(self):
        """Every recorded open question names an owner and a due phase."""
        content = read_optional(OPEN_QUESTIONS)
        assert content, f"The repository has no {OPEN_QUESTIONS}."

        sections = _sections(content)
        assert "Open" in sections, f"{OPEN_QUESTIONS} has no 'Open' section."

        rows = sections["Open"]
        assert rows, f"{OPEN_QUESTIONS} records no open question."

        header = rows[0]
        assert "Owner" in header, (
            f"{OPEN_QUESTIONS} has no owner column; every question must be owned."
        )
        owner_column = header.index("Owner")
        due_column = next(
            (index for index, cell in enumerate(header) if "Due" in cell), None
        )
        assert due_column is not None, (
            f"{OPEN_QUESTIONS} has no due-phase column; every question must have a "
            "due phase."
        )

        unowned = []
        for cells in rows[1:]:
            if len(cells) <= max(owner_column, due_column):
                continue
            identifier = cells[0]
            owner = cells[owner_column]
            due = cells[due_column]

            if owner.lower() in UNSET_OWNERS:
                unowned.append(f"{identifier} (no owner)")
                continue
            if not any(phase in due for phase in PHASES) and not re.search(
                r"\b\d{1,2}\b", due
            ):
                unowned.append(f"{identifier} (no due phase)")

        assert not unowned, (
            f"These open questions have no owner or no due phase: {unowned}"
        )

    def test_the_open_questions_document_names_its_purpose(self):
        """The document references the requirement it serves."""
        content = read(OPEN_QUESTIONS)
        assert "FR-027" in content, (
            f"{OPEN_QUESTIONS} does not reference the requirement it serves."
        )

    def test_no_resolved_question_is_still_open(self):
        """A question moved to 'Resolved' is not also listed as open."""
        sections = _sections(read(OPEN_QUESTIONS))
        open_ids = {cells[0] for cells in sections.get("Open", [])[1:]}
        resolved_ids = {cells[0] for cells in sections.get("Resolved", [])[1:]}

        assert not (open_ids & resolved_ids), (
            "These identifiers appear both as open and as resolved: "
            f"{sorted(open_ids & resolved_ids)}"
        )
