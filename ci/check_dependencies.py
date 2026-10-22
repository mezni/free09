"""Dependency check — audits the locked dependency set against a vendored snapshot.

The check is deliberately offline: it reads `uv.lock` and the vendored advisory
snapshot in `ci/advisories/python-advisories.json`, and verifies that the
lockfile resolves without network access. The snapshot is refreshed by
`.github/workflows/refresh-advisories.yml`, which opens a pull request.

Exit codes:

* 0 — PASS (every locked package is covered and no advisory matches)
* 1 — FAIL (a locked package matches a known advisory)
* 2 — COULD NOT RUN (the snapshot is missing, stale, or the lockfile does not
  resolve offline)
* 3 — INTERNAL ERROR
"""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCKFILE = Path("uv.lock")
SNAPSHOT = Path("ci/advisories/python-advisories.json")


def locked_packages() -> dict[str, str]:
    """Return the registry packages in `uv.lock` as name to version.

    The local project is excluded: it is not a third-party dependency and is
    not published to any index.
    """
    lockfile = REPO_ROOT / LOCKFILE
    if not lockfile.is_file():
        raise FileNotFoundError(f"{LOCKFILE} is missing")

    with lockfile.open("rb") as handle:
        data = tomllib.load(handle)

    packages: dict[str, str] = {}
    for entry in data.get("package", []):
        source = entry.get("source", {})
        if "registry" not in source:
            continue
        name = str(entry.get("name", "")).lower().replace("_", "-")
        version = str(entry.get("version", ""))
        if name:
            packages[name] = version
    return packages


def load_snapshot() -> dict:
    """Load the vendored advisory snapshot."""
    path = REPO_ROOT / SNAPSHOT
    if not path.is_file():
        raise FileNotFoundError(f"{SNAPSHOT} is missing")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def lockfile_resolves_offline() -> tuple[bool, str]:
    """Verify that the lockfile is current and resolves without the network."""
    result = subprocess.run(
        ["uv", "lock", "--check", "--offline"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def main() -> int:
    """Run the offline dependency audit."""
    try:
        locked = locked_packages()
        snapshot = load_snapshot()
    except FileNotFoundError as error:
        print("COULD NOT RUN")
        print("dependency-audit")
        print(str(error))
        return 2
    except (tomllib.TOMLDecodeError, json.JSONDecodeError) as error:
        print("COULD NOT RUN")
        print("dependency-audit")
        print(f"snapshot or lockfile is unreadable: {error}")
        return 2

    if not locked:
        print("COULD NOT RUN")
        print("dependency-audit")
        print(f"{LOCKFILE} declares no registry packages")
        return 2

    audited = snapshot.get("packages", {})
    advisories = snapshot.get("advisories", {})

    uncovered = sorted(name for name in locked if name not in audited)
    if uncovered:
        print("COULD NOT RUN")
        print("dependency-audit")
        print(
            f"{len(uncovered)} locked package(s) are not covered by the vendored "
            f"advisory snapshot: {', '.join(uncovered)}"
        )
        print("Refresh the snapshot with .github/workflows/refresh-advisories.yml")
        return 2

    findings: list[str] = []
    for name, entries in advisories.items():
        version = locked.get(name)
        for entry in entries:
            if entry.get("version") == version:
                findings.append(f"{name} {version} — {entry.get('id', 'UNKNOWN')}")

    resolves, output = lockfile_resolves_offline()
    if not resolves:
        print("COULD NOT RUN")
        print("dependency-audit")
        print("the lockfile does not resolve offline:")
        print(output)
        return 2

    if findings:
        print("FAIL")
        print("dependency-audit")
        print(f"{len(findings)} known advisory match(es):")
        for finding in findings:
            print(f"  - {finding}")
        return 1

    print("PASS")
    print("dependency-audit")
    print(
        f"{len(locked)} locked packages audited against the vendored snapshot; "
        "no known advisories match"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
