"""Traceability test — every requirement maps to a test that exists.

Test ID: `test_requirement_to_test_mapping_exists`
"""

import re

import pytest

from tests.governance.helpers import REPO_ROOT, markdown_tables, read

pytestmark = pytest.mark.governance

SPEC = "specs/001-project-setup/spec.md"
MATRIX = "docs/quality/traceability-matrix.md"

# The statuses a matrix row may carry.
IMPLEMENTED = {"Implemented", "Verified"}
KNOWN_STATUSES = IMPLEMENTED | {"Planned", "Stub", "Not started", "Proposed"}


def _spec_requirements() -> list[tuple[str, list[str]]]:
    """Return the requirements the specification states, with their test IDs."""
    content = read(SPEC)
    requirements: list[tuple[str, list[str]]] = []

    for match in re.finditer(
        r"^- \*\*(FR-\d{3}|BR-\d{3})\*\*:\s*(.+?)(?=^- \*\*|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    ):
        identifier, body = match.group(1), match.group(2)
        test_ids = re.findall(r"`(test_[A-Za-z0-9_]+)`", body)
        requirements.append((identifier, test_ids))

    return requirements


def _matrix_rows() -> list[dict[str, str]]:
    """Return the traceability matrix rows of the approved sections.

    The placeholder section is not a traceability claim — the matrix says so
    itself — so it is excluded.
    """
    content = read(MATRIX)
    approved = content.split("## Placeholder rows")[0]

    rows: list[dict[str, str]] = []

    for table in markdown_tables(approved):
        header = [cell.strip() for cell in table[0]]
        if not header or "Requirement ID" not in header:
            continue
        for row in table[1:]:
            if len(row) < len(header):
                continue
            rows.append(dict(zip(header, row, strict=False)))

    return rows


def _test_ids_in_tree() -> set[str]:
    """Return the test function names the repository defines."""
    found: set[str] = set()
    for path in sorted((REPO_ROOT / "tests").rglob("test_*.py")):
        content = path.read_text(encoding="utf-8")
        found.update(re.findall(r"def (test_[A-Za-z0-9_]+)", content))
    return found


class TestTraceabilityComplete:
    """The requirement-to-test mapping is complete and truthful."""

    def test_requirement_to_test_mapping_exists(self):
        """Every requirement the specification states has a matrix row."""
        requirements = _spec_requirements()
        assert requirements, "The specification states no requirement."

        rows = _matrix_rows()
        assert rows, f"{MATRIX} holds no requirement row."

        mapped = {row["Requirement ID"] for row in rows}
        unmapped = [
            identifier
            for identifier, _test_ids in requirements
            if identifier not in mapped
        ]
        assert not unmapped, f"These requirements have no traceability row: {unmapped}"

    def test_every_mapped_test_exists(self):
        """Every test the specification names exists in the tree."""
        available = _test_ids_in_tree()

        missing = []
        for identifier, test_ids in _spec_requirements():
            for test_id in test_ids:
                if test_id not in available:
                    missing.append(f"{identifier} -> {test_id}")

        assert not missing, f"These mapped tests do not exist in the tree: {missing}"

    def test_every_matrix_row_names_a_test_that_exists(self):
        """No matrix row names a test that does not exist."""
        available = _test_ids_in_tree()

        missing = []
        for row in _matrix_rows():
            test_id = row.get("Test ID", "").strip().strip("`")
            if not test_id:
                continue
            if test_id not in available:
                missing.append(f"{row.get('Requirement ID')} -> {test_id}")

        assert not missing, (
            f"These traceability rows name a test that does not exist: {missing}"
        )

    def test_no_row_is_still_planned(self):
        """No traceability row claims to be planned."""
        planned = [
            row["Requirement ID"]
            for row in _matrix_rows()
            if row.get("Status", "").strip() in {"Planned", "Not started"}
        ]
        assert not planned, (
            "These traceability rows still claim to be planned although the "
            f"artefacts exist: {planned}"
        )

    def test_the_statuses_are_known(self):
        """Every matrix row carries a status the repository defines."""
        unknown = [
            row.get("Requirement ID")
            for row in _matrix_rows()
            if row.get("Status", "").strip() not in KNOWN_STATUSES
        ]
        assert not unknown, (
            f"These traceability rows carry an unknown status: {unknown}"
        )
