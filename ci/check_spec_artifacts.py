"""Specification-artefact check — verifies the repository's governance artefacts.

Implements the `governance` required check defined in
`specs/001-project-setup/contracts/verification-contract.md`:

* templates carry unfilled placeholders only;
* exactly one constitution exists, with a governance record in `.specify/`;
* feature directories and their numbering are valid;
* the configuration contract and `.env.example` declare the same variables;
* the tracked tree matches the repository-layout contract;
* every relative link in a tracked Markdown document resolves.

Exit codes follow the repository contract:

* 0 — PASS
* 1 — FAIL (a violation was found)
* 2 — COULD NOT RUN (a required input is missing)
* 3 — INTERNAL ERROR
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CONSTITUTION_SOURCE = Path("docs/constitution.md")
CONSTITUTION_RECORD = Path(".specify/memory/constitution.md")
CONFIGURATION_CONTRACT = Path(
    "specs/001-project-setup/contracts/configuration-contract.md"
)
LAYOUT_CONTRACT = Path(
    "specs/001-project-setup/contracts/repository-layout-contract.md"
)
ENV_EXAMPLE = Path(".env.example")
TEMPLATES_DIR = Path("templates")
SPECS_DIR = Path("specs")

# A template placeholder is an angle-bracket token, an all-caps X/XXX run, or
# the date placeholder.
PLACEHOLDER_TOKEN = re.compile(r"<[^<>\n]+>|\bX{2,}\b|YYYY-MM-DD")

# A filled-in identifier that has no place in an unfilled template.
FILLED_IDENTIFIER = re.compile(r"\b(?:SPEC-\d{3}|ADR-\d{4})\b")

# A feature directory is `<three digits>-<slug>`.
FEATURE_DIR = re.compile(r"^(\d{3})-([a-z0-9]+(?:-[a-z0-9]+)*)$")

# A variable row in the configuration contract's declared-variable tables.
CONTRACT_VARIABLE = re.compile(
    r"^\|\s*`([A-Z][A-Z0-9_]*)`\s*\|\s*(Required|Optional|Reserved)\s*\|"
)

# A Markdown link target: the contents of `](...)`.
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

# Fenced code blocks hide example links that are not real references.
FENCE = re.compile(r"^\s*(```|~~~)")

# Top-level entries the repository-layout contract permits at the root.
ROOT_FILES = {
    ".dockerignore",
    ".env.example",
    ".gitleaks.toml",
    ".gitignore",
    ".pre-commit-config.yaml",
    ".python-version",
    "CONTRIBUTING.md",
    "Makefile",
    "README.md",
    "alembic.ini",
    "mypy.ini",
    "noxfile.py",
    "pyproject.toml",
    "uv.lock",
}

ROOT_DIRECTORIES = {
    ".github",
    ".opencode",
    ".specify",
    "ci",
    "deploy",
    "docs",
    "libs",
    "migrations",
    "scripts",
    "services",
    "specs",
    "src",
    "templates",
    "tests",
}


class GovernanceError(Exception):
    """Raised when the check cannot establish its preconditions."""


def _read(path: Path) -> str:
    """Read a repository file, or raise GovernanceError when it is absent."""
    full = REPO_ROOT / path
    if not full.is_file():
        raise GovernanceError(f"required file is missing: {path}")
    return full.read_text(encoding="utf-8")


def _tracked_files() -> list[str]:
    """Return the tracked file paths, relative to the repository root."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise GovernanceError("git ls-files failed; the tree is not a git repository")
    return [name for name in result.stdout.split("\0") if name]


def check_templates(violations: list[str]) -> None:
    """Templates must contain placeholders and no resolved identifiers."""
    templates_dir = REPO_ROOT / TEMPLATES_DIR
    if not templates_dir.is_dir():
        raise GovernanceError(f"required directory is missing: {TEMPLATES_DIR}")

    templates = sorted(templates_dir.glob("*.md"))
    if not templates:
        raise GovernanceError(f"no templates found in {TEMPLATES_DIR}")

    for template in templates:
        relative = template.relative_to(REPO_ROOT)
        content = template.read_text(encoding="utf-8")

        if not PLACEHOLDER_TOKEN.search(content):
            violations.append(
                f"{relative}: carries no unfilled placeholder; a template must "
                "be reusable and unfilled."
            )

        for match in FILLED_IDENTIFIER.finditer(content):
            violations.append(
                f"{relative}: contains the filled identifier '{match.group(0)}'; "
                "a template must not contain a resolved specification or ADR id."
            )


def check_constitution(violations: list[str]) -> None:
    """Exactly one constitution source exists, plus its governance record."""
    constitutions = sorted(
        path.relative_to(REPO_ROOT)
        for path in (REPO_ROOT / "docs").rglob("constitution.md")
    )
    if len(constitutions) != 1:
        violations.append(
            "expected exactly one constitution under docs/, found "
            f"{len(constitutions)}: {[str(p) for p in constitutions]}"
        )

    source = _read(CONSTITUTION_SOURCE)
    record = _read(CONSTITUTION_RECORD)

    source_articles = set(re.findall(r"^Art\. ([IVX]+)\. ", source, re.MULTILINE))
    record_articles = set(re.findall(r"^### Art\. ([IVX]+)\. ", record, re.MULTILINE))
    if source_articles != record_articles:
        violations.append(
            "the constitution source and its governance record disagree on the "
            f"articles: source={sorted(source_articles)}, "
            f"record={sorted(record_articles)}"
        )

    expected = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"}
    if source_articles != expected:
        violations.append(
            "the constitution must define Art. I through Art. XI, found "
            f"{sorted(source_articles)}"
        )

    for label, content in (("source", source), ("record", record)):
        if "[Principle content" in content or "YYYY-MM-DD" in content:
            violations.append(
                f"constitution {label} still carries an unfilled placeholder"
            )


def check_feature_directories(violations: list[str]) -> None:
    """Feature directories must be numbered uniquely and carry a specification."""
    specs_dir = REPO_ROOT / SPECS_DIR
    if not specs_dir.is_dir():
        raise GovernanceError(f"required directory is missing: {SPECS_DIR}")

    numbers: dict[str, Path] = {}
    for entry in sorted(specs_dir.iterdir()):
        if not entry.is_dir():
            continue

        match = FEATURE_DIR.match(entry.name)
        if not match:
            violations.append(
                f"{entry.relative_to(REPO_ROOT)}: feature directory must be named "
                "'<three digits>-<lowercase-slug>'."
            )
            continue

        number = match.group(1)
        if number in numbers:
            violations.append(
                f"{entry.relative_to(REPO_ROOT)}: feature number {number} is already "
                f"used by {numbers[number].relative_to(REPO_ROOT)}."
            )
        numbers[number] = entry

        if not (entry / "spec.md").is_file():
            violations.append(
                f"{entry.relative_to(REPO_ROOT)}: a feature directory must contain "
                "spec.md."
            )


def _contract_variables() -> dict[str, str]:
    """Return the variable name to marker mapping declared by the contract."""
    content = _read(CONFIGURATION_CONTRACT)
    variables: dict[str, str] = {}
    for line in content.splitlines():
        match = CONTRACT_VARIABLE.match(line.strip())
        if match:
            variables[match.group(1)] = match.group(2)
    if not variables:
        raise GovernanceError(
            f"no declared variables found in {CONFIGURATION_CONTRACT}"
        )
    return variables


def _example_variables() -> dict[str, str]:
    """Return the variable name to value mapping declared by `.env.example`."""
    content = _read(ENV_EXAMPLE)
    variables: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, _, value = stripped.partition("=")
        variables[name.strip()] = value.strip()
    if not variables:
        raise GovernanceError(f"no variables found in {ENV_EXAMPLE}")
    return variables


def check_configuration_contract(violations: list[str]) -> None:
    """The contract and `.env.example` MUST declare the same variables."""
    contract = _contract_variables()
    example = _example_variables()

    for name in sorted(set(example) - set(contract)):
        violations.append(
            f"Variable {name} in {ENV_EXAMPLE} is not declared in the "
            f"configuration contract {CONFIGURATION_CONTRACT}."
        )

    for name in sorted(set(contract) - set(example)):
        violations.append(
            f"Variable {name} is declared in the configuration contract "
            f"{CONFIGURATION_CONTRACT} but absent from {ENV_EXAMPLE}."
        )


def check_layout(violations: list[str]) -> None:
    """The tracked tree MUST match the repository-layout contract."""
    _read(LAYOUT_CONTRACT)

    for name in _tracked_files():
        top = name.split("/", 1)[0]
        if "/" in name:
            if top not in ROOT_DIRECTORIES:
                violations.append(
                    f"{name}: '{top}/' is not an entry of the repository-layout "
                    "contract's top-level ownership table."
                )
        elif top not in ROOT_FILES:
            violations.append(
                f"{name}: a root file that is not permitted by the "
                "repository-layout contract."
            )

    # A service owns its tests; the root tests directory does not.
    for path in (REPO_ROOT / "tests").rglob("test_*.py"):
        relative = path.relative_to(REPO_ROOT)
        if relative.parts[1] not in {"contract", "governance", "integration"}:
            violations.append(
                f"{relative}: the root tests/ directory holds cross-service "
                "contract tests and repository-governance tests only."
            )


def check_markdown_links(violations: list[str]) -> None:
    """Every relative link in a tracked Markdown document MUST resolve."""
    for name in _tracked_files():
        if not name.endswith(".md"):
            continue

        path = REPO_ROOT / name
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        in_fence = False
        for number, line in enumerate(content.splitlines(), start=1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            for target in MARKDOWN_LINK.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                relative = target.split("#", 1)[0]
                if not relative:
                    continue
                resolved = (path.parent / relative).resolve()
                if not resolved.exists():
                    violations.append(
                        f"{name}:{number}: link target '{target}' does not resolve."
                    )


def main() -> int:
    """Run every governance assertion and report the result."""
    violations: list[str] = []

    try:
        check_templates(violations)
        check_constitution(violations)
        check_feature_directories(violations)
        check_configuration_contract(violations)
        check_layout(violations)
        check_markdown_links(violations)
    except GovernanceError as error:
        print("COULD NOT RUN")
        print("governance")
        print(str(error))
        return 2
    except Exception as error:  # pragma: no cover - defensive
        print("INTERNAL ERROR")
        print("governance")
        print(f"{type(error).__name__}: {error}")
        return 3

    if violations:
        print("FAIL")
        print("governance")
        print(f"{len(violations)} violation(s) found:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print("PASS")
    print("governance")
    print(
        "templates, constitution, feature directories, configuration, layout, and "
        "document links agree"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
