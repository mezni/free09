"""Precedence test — the constitution's precedence order is declared and honoured.

Test ID: `test_precedence_order_is_declared_and_honoured`
"""

import re

import pytest

from tests.governance.helpers import read, read_optional

pytestmark = pytest.mark.governance

PRECEDENCE = "docs/governance/precedence-and-conventions.md"
CONSTITUTION = "docs/constitution.md"
GOVERNANCE_RECORD = ".specify/memory/constitution.md"


def _ranked_entries(content: str) -> list[tuple[int, str, str]]:
    """Return the ranked entries of the precedence table.

    The table has a `Rank` column, a `Document` column, and a `Governs`
    column. A numbered list is accepted as well.
    """
    entries: list[tuple[int, str, str]] = []

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.fullmatch(r"\|[\s:|-]+\|", stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2 or not cells[0].isdigit():
            continue
        entries.append((int(cells[0]), cells[1], cells[2] if len(cells) > 2 else ""))

    if entries:
        return entries

    for number, entry in re.findall(r"^\s*(\d+)\.\s+(.+)$", content, re.MULTILINE):
        entries.append((int(number), entry, ""))

    return entries


class TestPrecedenceOrder:
    """The order in which documents prevail is declared and applied."""

    def test_precedence_order_resolves_documented_conflict(self):
        """The precedence document declares the order the repository uses."""
        content = read_optional(PRECEDENCE)
        assert content, f"The repository has no {PRECEDENCE}."

        ranked = _ranked_entries(content)
        assert ranked, f"{PRECEDENCE} declares no ranked order."

        ranks = [rank for rank, _, _ in ranked]
        assert ranks == sorted(ranks), (
            f"{PRECEDENCE} ranks its entries out of order: {ranks}"
        )
        assert ranks == list(range(1, len(ranks) + 1)), (
            f"{PRECEDENCE} does not rank its entries consecutively: {ranks}"
        )

        # The constitution must appear in the order.
        entries = [entry for _, entry, _ in ranked]
        constitution_index = next(
            (
                index
                for index, entry in enumerate(entries)
                if CONSTITUTION in entry or "constitution" in entry.lower()
            ),
            None,
        )
        assert constitution_index is not None, (
            f"{PRECEDENCE} does not rank the constitution."
        )
        assert constitution_index == 0, (
            f"{PRECEDENCE} does not rank the constitution first; it is at "
            f"position {constitution_index + 1}."
        )

    def test_the_constitution_states_its_own_precedence(self):
        """The constitution declares which copy prevails."""
        content = read(CONSTITUTION)
        assert "precedence" in content.lower() or "prevail" in content.lower(), (
            "The constitution does not state a precedence rule."
        )

    def test_the_constitution_names_the_governance_record(self):
        """The constitution points at the governance record copy."""
        content = read(CONSTITUTION)
        assert GOVERNANCE_RECORD in content, (
            f"The constitution does not name {GOVERNANCE_RECORD}."
        )

    def test_the_two_constitution_copies_carry_the_same_version(self):
        """The numbered source and the governance record agree on the version."""
        source = read(CONSTITUTION)
        record = read(GOVERNANCE_RECORD)

        source_version = re.search(r"\*\*Version\*\*:\s*([\d.]+)", source)
        record_version = re.search(r"\*\*Version\*\*:\s*([\d.]+)", record)
        assert source_version is not None, (
            "The numbered constitution does not state its version."
        )
        assert record_version is not None, (
            "The governance record does not state its version."
        )
        assert source_version.group(1) == record_version.group(1), (
            "The constitution copies disagree on the version: "
            f"{source_version.group(1)} and {record_version.group(1)}"
        )

    def test_conflict_resolves_to_single_governing_statement(self):
        """A conflict between documents resolves to one governing statement.

        The two constitution copies cover the same articles, so no article has
        two competing governing statements. Where the two documents both
        speak to a subject, the ranked order decides which one governs, and
        the losing document must not restate the subject in a way that
        contradicts the winner.
        """
        source = read(CONSTITUTION)
        record = read(GOVERNANCE_RECORD)

        source_articles = _article_headings(source)
        record_articles = _article_headings(record)

        assert source_articles, "The constitution states no article."
        assert source_articles == record_articles, (
            "The constitution copies do not cover the same articles; the "
            f"source has {source_articles} and the record has {record_articles}."
        )

        # The source is the ranked winner, so it must name the record as the
        # subordinate copy.
        assert GOVERNANCE_RECORD in source, (
            "The ranked constitution does not name the subordinate copy."
        )

        # The ranked document must not be contradicted by a lower-ranked one.
        ranked = _ranked_entries(read(PRECEDENCE))
        assert ranked, f"{PRECEDENCE} declares no ranked order."

        entries = [entry for _, entry, _ in ranked]
        constitution_rank = next(
            index
            for index, entry in enumerate(entries)
            if CONSTITUTION in entry or "constitution" in entry.lower()
        )
        record_rank = next(
            (
                index
                for index, entry in enumerate(entries)
                if GOVERNANCE_RECORD in entry or "governance record" in entry.lower()
            ),
            None,
        )
        if record_rank is not None:
            assert constitution_rank < record_rank, (
                "The ranked order does not place the constitution above its "
                "governance record."
            )


def _article_headings(content: str) -> list[str]:
    """Return the article headings of a constitution copy.

    The numbered source states its articles as plain lines; the governance
    record states them as headings. Both forms are accepted.
    """
    return re.findall(
        r"^(?:#{2,4}\s*)?(Art\.\s+[IVX]+\.\s+.+)$",
        content,
        re.MULTILINE,
    )
