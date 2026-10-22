"""Refresh the vendored advisory snapshot from a `pip-audit` JSON report.

Usage:

    pip-audit --strict --format=json -r <requirements> > audit.json
    python ci/refresh_advisories.py audit.json

The snapshot lists every registry package in `uv.lock` with its locked
version, plus the advisories that apply to it. `ci/check_dependencies.py`
compares the locked set against the snapshot offline and never touches the
network.
"""

import json
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCKFILE = Path("uv.lock")
SNAPSHOT = Path("ci/advisories/python-advisories.json")


def locked_packages() -> dict[str, str]:
    """Return the registry packages in `uv.lock` as name to version."""
    with (REPO_ROOT / LOCKFILE).open("rb") as handle:
        data = tomllib.load(handle)

    packages: dict[str, str] = {}
    for entry in data.get("package", []):
        if "registry" not in entry.get("source", {}):
            continue
        name = str(entry.get("name", "")).lower().replace("_", "-")
        if name:
            packages[name] = str(entry.get("version", ""))
    return packages


def main() -> int:
    """Rebuild the snapshot from the supplied pip-audit report."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <pip-audit-report.json>", file=sys.stderr)
        return 2

    report_path = Path(sys.argv[1])
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read the pip-audit report: {error}", file=sys.stderr)
        return 2

    locked = locked_packages()
    advisories: dict[str, list[dict]] = {}
    audited: set[str] = set()

    for dependency in report.get("dependencies", []):
        name = str(dependency.get("name", "")).lower().replace("_", "-")
        audited.add(name)
        vulnerabilities = dependency.get("vulns") or []
        if vulnerabilities:
            advisories[name] = [
                {
                    "id": vulnerability.get("id", "UNKNOWN"),
                    "version": dependency.get("version", ""),
                    "fix_versions": vulnerability.get("fix_versions", []),
                }
                for vulnerability in vulnerabilities
            ]

    snapshot = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "pip-audit --strict --format=json over the locked dependency set",
        "note": (
            "Vendored advisory snapshot. `ci/check_dependencies.py` matches the "
            "locked dependency set against this file offline and never touches the "
            "network. Regenerate it with .github/workflows/refresh-advisories.yml."
        ),
        "packages": {
            name: {"version": version} for name, version in sorted(locked.items())
        },
        "advisories": advisories,
        "not_audited": sorted(set(locked) - audited),
    }

    target = REPO_ROOT / SNAPSHOT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"wrote {SNAPSHOT}: {len(locked)} packages, {len(advisories)} with advisories"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
