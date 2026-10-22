"""Layout test — the repository layout matches the documented structure.

Test ID: `test_repository_layout_matches_documented_structure`
"""

import pytest

from tests.governance.helpers import REPO_ROOT, markdown_tables, read, tracked_files

pytestmark = pytest.mark.governance

LAYOUT_CONTRACT = "specs/001-project-setup/contracts/repository-layout-contract.md"


def _contract_paths() -> list[str]:
    """Return the paths the layout contract's path tables name."""
    content = read(LAYOUT_CONTRACT)
    paths: list[str] = []

    for table in markdown_tables(content):
        header = [cell.strip() for cell in table[0]]
        if not header or header[0] != "Path":
            continue
        for row in table[1:]:
            candidate = row[0].strip().strip("`")
            if not candidate:
                continue
            paths.append(candidate)

    return paths


class TestRepositoryLayout:
    """The tree matches the layout contract and the documented structure."""

    def test_repository_layout_matches_documented_structure(self):
        """Every path the layout contract names exists in the tree."""
        missing = [
            path
            for path in _contract_paths()
            if not path.endswith("/") and not (REPO_ROOT / path).exists()
        ]
        assert not missing, (
            f"The layout contract names paths that do not exist in the tree: {missing}"
        )

    def test_contract_covers_every_top_level_entry(self):
        """Every tracked top-level entry is named by the layout contract."""
        content = read(LAYOUT_CONTRACT)
        top_level = sorted(
            {name.split("/", 1)[0] for name in tracked_files()} - {"__pycache__"}
        )
        undocumented = [name for name in top_level if name not in content]
        assert not undocumented, (
            f"The layout contract does not name these top-level entries: {undocumented}"
        )

    def test_readme_documents_the_same_structure(self):
        """The README's structure table lists the same top-level entries."""
        readme = read("README.md")
        for entry in ("specs/", "docs/", "ci/", "tests/", "src/"):
            assert entry in readme, f"README.md does not document {entry}"
