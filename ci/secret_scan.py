"""Secret scanner — scans tracked files for committed credentials.

Exits 0 when no likely secret is found, 1 when a finding requires attention.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Patterns that indicate a hard-coded credential rather than a placeholder.
PATTERNS = [
    (
        "aws-access-key-id",
        re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ),
    (
        "private-key-block",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    ),
    (
        "github-token",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    ),
    (
        "slack-token",
        re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    ),
    (
        "assigned-secret",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret[_-]?key|password|passwd|token)"
            r"\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']"
        ),
    ),
]

# Values that are explicitly documented placeholders and therefore safe.
PLACEHOLDER_MARKERS = (
    "PLACEHOLDER",
    "CHANGE_ME",
    "CHANGEME",
    "example",
    "EXAMPLE",
    "dummy",
    "DUMMY",
    "xxxxxxxx",
    "your-",
    "YOUR_",
    "<",
    "${",
    "test-jwt-token",
    "redacted",
    "REDACTED",
)

SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz"}
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".specify", "graphify-out"}


def _is_placeholder(line: str) -> bool:
    return any(marker in line for marker in PLACEHOLDER_MARKERS)


def _tracked_files() -> list[Path]:
    """List files tracked by git, falling back to a filesystem walk."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout:
        names = [n for n in result.stdout.split("\0") if n]
        return [REPO_ROOT / name for name in names]

    return [
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file() and not any(part in SKIP_DIRS for part in path.parts)
    ]


def scan() -> list[tuple[str, int, str, str]]:
    """Return findings as (relative path, line number, rule name, snippet)."""
    findings: list[tuple[str, int, str, str]] = []

    for path in _tracked_files():
        if path.suffix.lower() in SKIP_SUFFIXES or not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for number, line in enumerate(content.splitlines(), start=1):
            if _is_placeholder(line):
                continue
            for rule, pattern in PATTERNS:
                if pattern.search(line):
                    snippet = line.strip()[:120]
                    findings.append(
                        (str(path.relative_to(REPO_ROOT)), number, rule, snippet)
                    )

    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("Secret scan FAILED — possible committed credentials:")
        for path, number, rule, snippet in findings:
            print(f"  - {path}:{number} [{rule}] {snippet}")
        return 1

    print("Secret scan PASSED — no committed credentials detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
