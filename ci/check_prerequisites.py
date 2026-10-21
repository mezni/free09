"""Prerequisite verifier — T029 [US1].

Checks Python, uv, Docker, git, and make versions against the documented
baseline and names each missing prerequisite. Exits with code 2 if any
required prerequisite is missing, which the gate checks treat as a failure.
"""

import re
import subprocess
import sys

REQUIRED = [
    ("uv", "0.12.15", "UV workspace manager"),
    ("docker", None, "Docker daemon"),
    ("git", None, "Git version control"),
    ("make", None, "Make build tool"),
]

# Interpreters are looked up under every accepted name, in order.
PYTHON_COMMANDS = ("python3", "python")


def _version_tuple(value: str) -> tuple:
    return tuple(int(part) for part in value.split("."))


def check_prerequisites() -> list[str]:
    """Return a list of human-readable failures; empty when all prerequisites pass."""
    failures: list[str] = []

    for cmd, min_version, description in REQUIRED:
        failures.extend(_check_command(cmd, min_version, description))

    failures.extend(_check_python())
    return failures


def _check_command(cmd: str, min_version: str | None, description: str) -> list[str]:
    """Check a single command, returning any failure descriptions."""
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except FileNotFoundError:
        return [f"{description}: command not found"]
    except subprocess.TimeoutExpired:
        return [f"{description}: command not found or timed out"]

    if result.returncode != 0:
        return [f"{description}: command not found"]

    if not min_version:
        return []

    version_match = re.search(r"(\d+\.\d+(?:\.\d+)*)", result.stdout.strip())
    if version_match:
        found = version_match.group(1)
        if _version_tuple(found) < _version_tuple(min_version):
            return [f"{description}: {found} < required {min_version}"]

    return []


def _check_python() -> list[str]:
    """Check for a Python 3.13+ interpreter under any accepted command name."""
    for cmd in PYTHON_COMMANDS:
        failures = _check_command(cmd, "3.13", "Python interpreter")
        if not failures:
            return []
        if "command not found" not in failures[0]:
            return failures

    return [f"Python interpreter: none of {', '.join(PYTHON_COMMANDS)} were found"]


def main() -> int:
    """Run the prerequisite check and return the process exit code."""
    failures = check_prerequisites()
    if failures:
        print("Prerequisite check FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 2

    print("Prerequisite check PASSED — all required prerequisites present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
