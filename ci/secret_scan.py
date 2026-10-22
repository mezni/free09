"""Secret scanner — scans the tracked tree and the version-controlled history.

Implements the `secret-scan` required check defined in
`specs/001-project-setup/contracts/verification-contract.md`:

* no secret material exists in the working tree or anywhere in the
  version-controlled history (FR-017);
* no detected value is ever printed — every match is redacted in stdout and
  in the JSON report alike (FR-018).

Exit codes:

* 0 — PASS
* 1 — FAIL (a finding requires attention)
* 2 — COULD NOT RUN (git is unavailable, or the tree is not a repository)
* 3 — INTERNAL ERROR
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECK_ID = "secret-scan"

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

REDACTED = "***REDACTED***"


class ScanError(Exception):
    """Raised when the scan cannot establish its preconditions."""


def _is_placeholder(line: str) -> bool:
    """Return True when the line is a documented placeholder."""
    return any(marker in line for marker in PLACEHOLDER_MARKERS)


def _redact(line: str, pattern: re.Pattern[str]) -> str:
    """Return the line with every matched value replaced by a redaction marker."""
    return pattern.sub(REDACTED, line)


def _git(*args: str) -> str:
    """Run a git command in the repository and return its stdout."""
    result = _git_raw(*args)
    if result.returncode != 0:
        raise ScanError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def _git_raw(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    """Run a git command in the repository and return the completed process."""
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=text,
        check=False,
    )


def _git_bytes(*args: str) -> bytes:
    """Run a git command and return its raw stdout.

    Binary payloads in the history are not valid UTF-8; they are decoded with
    replacement characters so that the scan does not abort on them.
    """
    result = _git_raw(*args, text=False)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", "replace").strip()
        raise ScanError(f"git {' '.join(args)} failed: {stderr}")
    return result.stdout


def _tracked_files() -> list[str]:
    """Return the tracked file paths, relative to the repository root."""
    try:
        output = _git("ls-files", "-z")
    except ScanError as error:
        raise ScanError(f"the tree is not a git repository: {error}") from error
    return [name for name in output.split("\0") if name]


def _commits() -> list[str]:
    """Return every commit reachable from any ref."""
    try:
        output = _git("rev-list", "--all")
    except ScanError as error:
        raise ScanError(f"the history cannot be read: {error}") from error
    return [line for line in output.splitlines() if line]


def _scan_text(content: str, location: str, findings: list[dict[str, object]]) -> None:
    """Scan text for secrets, appending redacted findings."""
    for number, line in enumerate(content.splitlines(), start=1):
        if _is_placeholder(line):
            continue
        for rule, pattern in PATTERNS:
            match = pattern.search(line)
            if match is None:
                continue
            findings.append(
                {
                    "location": f"{location}:{number}",
                    "rule": rule,
                    "secret": REDACTED,
                    "match": _redact(line.strip()[:120], pattern),
                }
            )


def scan_tree() -> list[dict[str, object]]:
    """Scan every tracked file in the working tree."""
    findings: list[dict[str, object]] = []

    for name in _tracked_files():
        path = REPO_ROOT / name
        if Path(name).suffix.lower() in SKIP_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in Path(name).parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        _scan_text(content, name, findings)

    return findings


HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def scan_history() -> list[dict[str, object]]:
    """Scan every line ever added to or removed from the version-controlled history.

    The history is read as a single unified diff so that the same Python
    patterns that scan the working tree also apply to the history. This keeps
    the scan portable: it does not depend on `git grep -P` being available.
    """
    try:
        raw = _git_bytes("log", "--all", "-p", "--no-color", "-U0")
    except ScanError as error:
        raise ScanError(f"the history cannot be read: {error}") from error

    output = raw.decode("utf-8", errors="replace")

    findings: list[dict[str, object]] = []
    path = "unknown"
    line_number = 0

    for line in output.splitlines():
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path == "/dev/null":
                path = "removed"
            continue
        if line.startswith("--- "):
            continue
        if line.startswith("diff --git "):
            path = "unknown"
            line_number = 0
            continue
        hunk = HUNK.match(line)
        if hunk is not None:
            line_number = int(hunk.group(1))
            continue

        if line.startswith("+"):
            content = line[1:]
            _scan_text(content, f"{path}:{line_number}", findings)
            line_number += 1
        elif line.startswith("-"):
            content = line[1:]
            _scan_text(content, f"{path} (removed line)", findings)

    return findings


def main() -> int:
    """Run the secret scan and report the result."""
    try:
        findings = scan_tree() + scan_history()
    except ScanError as error:
        print("COULD NOT RUN")
        print(CHECK_ID)
        print(str(error))
        return 2
    except Exception as error:  # pragma: no cover - defensive
        print("INTERNAL ERROR")
        print(CHECK_ID)
        print(f"{type(error).__name__}: {error}")
        return 3

    if findings:
        print("FAIL")
        print(CHECK_ID)
        print(
            f"{len(findings)} finding(s) require attention. Every value is "
            "redacted; see the report for the locations."
        )
        for finding in findings:
            print(
                f"  - {finding['location']} [{finding['rule']}] "
                f"secret={finding['secret']} match={finding['match']}"
            )
        print(json.dumps(findings, indent=2, sort_keys=True))
        return 1

    print("PASS")
    print(CHECK_ID)
    print(
        "no secret material found in the working tree or the version-controlled history"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
