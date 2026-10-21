"""Dependency audit — audits locked third-party dependencies for advisories.

Exports the locked dependency set (excluding the local project) and runs
`pip-audit` against it. Exits 0 when no known vulnerability is found.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        **kwargs,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        requirements = Path(tmpdir) / "requirements.txt"

        export = _run(
            [
                "uv",
                "export",
                "--no-emit-project",
                "--no-hashes",
                "--format",
                "requirements-txt",
                "--output-file",
                str(requirements),
            ]
        )
        if export.returncode != 0:
            print("Dependency audit COULD NOT RUN — unable to export dependencies")
            print(export.stderr.strip() or export.stdout.strip())
            return 2

        audit = _run(["pip-audit", "--strict", "-r", str(requirements)])
        output = (audit.stdout + audit.stderr).strip()

        if audit.returncode == 0:
            print(output or "Dependency audit PASSED — no known vulnerabilities found")
            return 0

        if "no known vulnerabilities" in output.lower():
            print("Dependency audit PASSED — no known vulnerabilities found")
            return 0

        print("Dependency audit FAILED — known vulnerabilities detected:")
        print(output)
        return 1


if __name__ == "__main__":
    sys.exit(main())
