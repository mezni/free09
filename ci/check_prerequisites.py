"""Prerequisite verifier — T029 [US1].

Checks Python, uv, Docker, git, and make versions against the documented
baseline and names each missing prerequisite. Exits with code 2 if any
required prerequisite is missing, which the gate checks treat as a failure.
"""

import subprocess
import sys
import re

REQUIRED = [
    ("python", "3.13", "Python interpreter"),
    ("uv", "0.12.15", "UV workspace manager"),
    ("docker", None, "Docker daemon"),
    ("git", None, "Git version control"),
    ("make", None, "Make build tool"),
]

MISSING = []
FAILURES = []

for cmd, min_version, description in REQUIRED:
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            MISSING.append(description)
            FAILURES.append(f"{description}: command not found")
            continue

        version_output = result.stdout.strip()
        # Extract version number from output
        # Patterns: "python 3.13.7", "uv 0.12.15", "git version 2.34.1"
        version_match = re.search(r"(\d+\.\d+(?:\.\d+)*)", version_output)
        if version_match:
            found_version = version_match.group(1)
            if min_version and version_match.group(1):
                # Simple version comparison
                if found_version < min_version:
                    MISSING.append(description)
                    FAILURES.append(
                        f"{description}: {found_version} < required {min_version}"
                    )
            else:
                # No minimum version check (Docker, git, make)
                pass  # Present, version noted but not validated against minimum
        else:
            # Couldn't parse version — still count as present
            pass

    except (FileNotFoundError, subprocess.TimeoutExpired):
        MISSING.append(description)
        FAILURES.append(f"{description}: command not found or timed out")

# Report results
if MISSING:
    print("Prerequisite check FAILED — missing prerequisites:", ", ".join(MISSING))
    for failure in FAILURES:
        print(f"  - {failure}")
    sys.exit(2)
else:
    print("Prerequisite check PASSED — all required prerequisites present")
    sys.exit(0)
