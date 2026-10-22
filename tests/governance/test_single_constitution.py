"""Constitution test — exactly one constitution, ratified, with an amendment route.

Test ID: `test_single_constitution_with_version_and_ratification`
"""

import re
from pathlib import Path

import pytest

from tests.governance.helpers import REPO_ROOT

pytestmark = pytest.mark.governance

ARTICLES = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI")


def _constitutions() -> list[Path]:
    """Return every constitution document under `docs/`."""
    docs_dir = REPO_ROOT / "docs"
    if not docs_dir.is_dir():
        return []
    return sorted(docs_dir.rglob("constitution.md"))


class TestSingleConstitution:
    """The repository has one constitution, and it is in force."""

    def test_single_constitution_with_version_and_ratification(self):
        """One constitution exists, states its version, and is ratified."""
        constitutions = _constitutions()
        found = [path.name for path in constitutions]
        assert len(constitutions) == 1, (
            f"Expected exactly one constitution under docs/, found "
            f"{len(constitutions)}: {found}"
        )

        content = constitutions[0].read_text(encoding="utf-8")

        assert re.search(r"^\*{0,2}Version\*{0,2}:\s*\S+", content, re.MULTILINE), (
            "The constitution states no version."
        )
        assert re.search(r"^\*{0,2}Status\*{0,2}:\s*Ratified", content, re.MULTILINE), (
            "The constitution is not ratified."
        )
        assert re.search(
            r"^\*{0,2}Ratified\*{0,2}:\s*\d{4}-\d{2}-\d{2}",
            content,
            re.MULTILINE,
        ), "The constitution states no ratification date."
        assert "amend" in content.lower(), (
            "The constitution states no amendment procedure."
        )

    def test_constitution_defines_every_article(self):
        """The constitution defines Art. I through Art. XI."""
        content = _constitutions()[0].read_text(encoding="utf-8")
        articles = set(re.findall(r"^Art\. ([IVX]+)\.", content, re.MULTILINE))
        assert articles == set(ARTICLES), (
            f"The constitution defines {sorted(articles)}, not {sorted(ARTICLES)}."
        )

    def test_the_governance_record_agrees_with_the_source(self):
        """The governance record mirrors the constitution's articles."""
        record = REPO_ROOT / ".specify" / "memory" / "constitution.md"
        assert record.is_file(), "The constitution's governance record is missing."

        source = _constitutions()[0].read_text(encoding="utf-8")
        record_content = record.read_text(encoding="utf-8")

        source_articles = set(re.findall(r"^Art\. ([IVX]+)\.", source, re.MULTILINE))
        record_articles = set(
            re.findall(r"^### Art\. ([IVX]+)\.", record_content, re.MULTILINE)
        )
        assert source_articles == record_articles, (
            "The constitution and its governance record disagree on the articles: "
            f"{sorted(source_articles)} versus {sorted(record_articles)}."
        )
