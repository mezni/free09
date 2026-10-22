"""Shared helpers for the governance test suite.

The helpers here are deliberately boring: they read the repository's own
artefacts so that a test can assert a property of the tree rather than a
property of a copy of the tree.
"""

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# A feature directory: a zero-padded number and a kebab-case name.
FEATURE_DIR = re.compile(r"^(\d{3})-([a-z0-9]+(?:-[a-z0-9]+)*)$")

# A filled identifier that must never appear in a template.
FILLED_IDENTIFIER = re.compile(r"\b(?:SPEC-\d{3}|ADR-\d{4})\b")

# An unfilled placeholder.
PLACEHOLDER = re.compile(r"<[^<>\n]+>|\bX{2,}\b|YYYY-MM-DD|\[P\]|T\d{3}")

# The nine required checks, in lane order.
REQUIRED_CHECKS = [
    "format",
    "lint",
    "lockfile",
    "governance",
    "file-coverage",
    "typecheck",
    "test",
    "secret-scan",
    "dependency-audit",
]

VERIFICATION_CONTRACT = "specs/001-project-setup/contracts/verification-contract.md"
WORKFLOW = ".github/workflows/ci.yml"


def _is_separator(row: list[str]) -> bool:
    """Return True when the row is a markdown table separator."""
    return bool(row) and all(cell and set(cell) <= set("-: ") for cell in row)


def contract_check_table() -> list[dict[str, str]]:
    """Return the verification contract's check table as a list of rows."""
    content = read(VERIFICATION_CONTRACT)
    rows: list[dict[str, str]] = []

    for table in markdown_tables(content):
        header = [cell.strip() for cell in table[0]]
        if not header or header[0] != "ID":
            continue
        for row in table[1:]:
            if len(row) < len(header):
                continue
            rows.append(dict(zip(header, row, strict=False)))

    return rows


def read(path: str) -> str:
    """Return the text of a repository file."""
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def read_optional(path: str) -> str:
    """Return the text of a repository file, or an empty string when absent."""
    full = REPO_ROOT / path
    if not full.is_file():
        return ""
    return full.read_text(encoding="utf-8")


def git(*args: str) -> subprocess.CompletedProcess:
    """Run a git command in the repository and return the completed process."""
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def tracked_files() -> list[str]:
    """Return the tracked file paths, relative to the repository root."""
    result = git("ls-files", "-z")
    if result.returncode != 0:
        return []
    return [name for name in result.stdout.split("\0") if name]


def feature_directories() -> list[Path]:
    """Return the feature directories under `specs/`, sorted by number."""
    specs_dir = REPO_ROOT / "specs"
    if not specs_dir.is_dir():
        return []
    directories = [
        entry
        for entry in specs_dir.iterdir()
        if entry.is_dir() and FEATURE_DIR.match(entry.name)
    ]
    return sorted(directories, key=lambda path: path.name)


def markdown_tables(content: str) -> list[list[list[str]]]:
    """Return every markdown table in the content as a list of rows of cells.

    Each table is a list of rows; the first row is the header. Separator rows
    are removed. A row is a list of cell strings with the surrounding
    whitespace removed.
    """
    tables: list[list[list[str]]] = []
    group: list[list[str]] = []

    def _flush() -> None:
        rows = [row for row in group if not _is_separator(row)]
        if rows:
            tables.append(rows)

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            group.append([cell.strip() for cell in stripped.strip("|").split("|")])
            continue
        if group:
            _flush()
            group = []

    if group:
        _flush()

    return tables
