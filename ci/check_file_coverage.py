"""File-coverage check — every tracked file must be covered by a required check.

Reads the declaration in `ci/file-coverage.yml` and verifies:

* every tracked file matches at least one declared coverage glob;
* every exclusion carries a reason, an owner, and an unexpired review date;
* every declared check exists as a nox session and as a CI job;
* every declared check appears in the CI workflow and in the gate's lane;
* the gate job depends on both lanes, runs under `if: always()`, and does not
  use `continue-on-error`;
* every action in the workflow is pinned to a full 40-character commit SHA.

Exit codes:

* 0 — PASS
* 1 — FAIL (a violation was found)
* 2 — COULD NOT RUN (the declaration, the tree, or the workflow is missing)
* 3 — INTERNAL ERROR
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

DECLARATION = Path("ci/file-coverage.yml")
WORKFLOW = Path(".github/workflows/ci.yml")

LANE_JOBS = {"fast-checks", "slow-checks"}
GATE_JOB = "required-checks"

# A `uses:` entry pinned to a full commit SHA.
ACTION_USE = re.compile(r"^\s*uses:\s*([^\s#]+)")
SHA = re.compile(r"^[0-9a-f]{40}$")

# A nox session declaration, with an optional explicit name.
SESSION = re.compile(
    r"^@nox\.session\((?P<args>[^)]*)\)\s*\n(?:[^\n]*\n)?def\s+(?P<func>\w+)\s*\(",
    re.MULTILINE,
)
SESSION_NAME = re.compile(r"""name=["'](?P<name>[^"']+)["']""")


class CoverageError(Exception):
    """Raised when the check cannot establish its preconditions."""


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
        raise CoverageError("git ls-files failed; the tree is not a git repository")
    return [name for name in result.stdout.split("\0") if name]


def _load_declaration() -> dict:
    """Load and validate the coverage declaration."""
    path = REPO_ROOT / DECLARATION
    if not path.is_file():
        raise CoverageError(f"required file is missing: {DECLARATION}")
    with path.open(encoding="utf-8") as handle:
        declaration = yaml.safe_load(handle)
    if not isinstance(declaration, dict) or "checks" not in declaration:
        raise CoverageError(f"{DECLARATION} does not declare a 'checks' mapping")
    return declaration


def _matches(path: str, glob: str) -> bool:
    """Match a repository-relative path against a coverage glob."""
    import fnmatch

    if glob == "**/*":
        return True
    if fnmatch.fnmatch(path, glob):
        return True
    # `**/` also matches zero directories.
    if glob.startswith("**/") and fnmatch.fnmatch(path, glob[3:]):
        return True
    # A directory glob covers everything beneath it.
    return bool(glob.endswith("/**") and path.startswith(glob[:-3]))


def _nox_sessions() -> set[str]:
    """Return the nox session names declared in `noxfile.py`."""
    noxfile = REPO_ROOT / "noxfile.py"
    if not noxfile.is_file():
        raise CoverageError("noxfile.py is missing")
    content = noxfile.read_text(encoding="utf-8")

    sessions: set[str] = set()
    for match in SESSION.finditer(content):
        name_match = SESSION_NAME.search(match.group("args"))
        sessions.add(name_match.group("name") if name_match else match.group("func"))
    return sessions


def _workflow_jobs() -> dict[str, str]:
    """Return the CI workflow's job id to job body mapping."""
    path = REPO_ROOT / WORKFLOW
    if not path.is_file():
        raise CoverageError(f"required file is missing: {WORKFLOW}")
    content = path.read_text(encoding="utf-8")

    jobs: dict[str, str] = {}
    lines = content.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.rstrip() == "jobs:":
            start = index + 1
            break
    if start is None:
        raise CoverageError(f"{WORKFLOW} declares no 'jobs:' mapping")

    current: str | None = None
    body: list[str] = []
    for line in lines[start:]:
        job = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if job:
            if current:
                jobs[current] = "\n".join(body)
            current = job.group(1)
            body = []
        elif current is not None:
            body.append(line)
    if current:
        jobs[current] = "\n".join(body)
    return jobs


def check_coverage(declaration: dict, violations: list[str]) -> None:
    """Every tracked file must be covered by a declared check or excluded."""
    checks = declaration["checks"]
    exclusions = declaration.get("exclusions", [])

    covered_globs = [glob for check in checks.values() for glob in check["covers"]]

    excluded_globs: list[str] = []
    for exclusion in exclusions:
        excluded_globs.extend(exclusion.get("paths", []))

    for path in _tracked_files():
        if any(_matches(path, glob) for glob in covered_globs):
            continue
        if any(_matches(path, glob) for glob in excluded_globs):
            continue
        violations.append(
            f"{path}: not covered by a required check and not excluded; add a "
            f"coverage glob to {DECLARATION} or a justified exclusion."
        )


def check_exclusions(declaration: dict, violations: list[str]) -> None:
    """Every exclusion must be justified and must not have expired."""
    today = date.today()
    for exclusion in declaration.get("exclusions", []):
        reason = exclusion.get("reason", "").strip()
        owner = exclusion.get("owner", "").strip()
        review_by = str(exclusion.get("review_by", "")).strip()

        if not reason:
            violations.append("an exclusion carries no reason")
        if not owner:
            violations.append("an exclusion carries no owner")
        if not review_by:
            violations.append("an exclusion carries no review date")
            continue
        try:
            expiry = date.fromisoformat(review_by)
        except ValueError:
            violations.append(
                f"an exclusion has an unparsable review date: {review_by}"
            )
            continue
        if expiry < today:
            violations.append(
                f"an exclusion expired on {review_by} and must be renewed or the "
                "file must be covered by a required check"
            )


def check_sessions(declaration: dict, violations: list[str]) -> None:
    """Every declared check must exist as a nox session."""
    sessions = _nox_sessions()
    for check_id, check in declaration["checks"].items():
        session = check.get("session", check_id)
        if session not in sessions:
            violations.append(
                f"check '{check_id}' declares session '{session}', which is not "
                f"defined in noxfile.py (known sessions: {sorted(sessions)})"
            )


def check_workflow(declaration: dict, violations: list[str]) -> None:
    """Every declared check must be a CI job, and the gate must fail closed."""
    jobs = _workflow_jobs()
    content = (REPO_ROOT / WORKFLOW).read_text(encoding="utf-8")

    for job_id in sorted(LANE_JOBS | {GATE_JOB}):
        if job_id not in jobs:
            violations.append(f"{WORKFLOW} does not define the '{job_id}' job")

    for check_id, check in declaration["checks"].items():
        lane = check.get("lane")
        if lane not in jobs:
            violations.append(
                f"check '{check_id}' declares lane '{lane}', which is not a job "
                f"in {WORKFLOW}"
            )
            continue
        if check_id not in jobs[lane]:
            violations.append(
                f"check '{check_id}' is not run by the '{lane}' job in {WORKFLOW}"
            )

    if GATE_JOB in jobs:
        gate = jobs[GATE_JOB]
        needs = re.search(r"^\s*needs:\s*\[(.*)\]\s*$", gate, re.MULTILINE)
        if not needs:
            violations.append(f"the '{GATE_JOB}' job declares no 'needs:' list")
        else:
            declared = {item.strip().strip("\"'") for item in needs.group(1).split(",")}
            missing = sorted(LANE_JOBS - declared)
            if missing:
                violations.append(f"the '{GATE_JOB}' gate does not depend on {missing}")
        if "if: always()" not in gate:
            violations.append(
                f"the '{GATE_JOB}' gate does not run under 'if: always()'; a "
                "skipped lane would read as a pass"
            )
        if "continue-on-error" in gate:
            violations.append(
                f"the '{GATE_JOB}' gate uses 'continue-on-error'; a failing lane "
                "would stop blocking the merge"
            )

    if "pull_request_target" in content:
        violations.append(f"{WORKFLOW} uses 'pull_request_target'")

    for line in content.splitlines():
        match = ACTION_USE.match(line)
        if not match:
            continue
        reference = match.group(1)
        if reference.startswith("./") or reference.startswith("docker://"):
            continue
        if "@" not in reference:
            violations.append(f"action '{reference}' is not pinned to a commit SHA")
            continue
        digest = reference.rsplit("@", 1)[1]
        if not SHA.match(digest):
            violations.append(
                f"action '{reference}' is not pinned to a full 40-character commit SHA"
            )


def main() -> int:
    """Run every file-coverage assertion and report the result."""
    violations: list[str] = []

    try:
        declaration = _load_declaration()
        check_coverage(declaration, violations)
        check_exclusions(declaration, violations)
        check_sessions(declaration, violations)
        check_workflow(declaration, violations)
    except CoverageError as error:
        print("COULD NOT RUN")
        print("file-coverage")
        print(str(error))
        return 2
    except Exception as error:  # pragma: no cover - defensive
        print("INTERNAL ERROR")
        print("file-coverage")
        print(f"{type(error).__name__}: {error}")
        return 3

    if violations:
        print("FAIL")
        print("file-coverage")
        print(f"{len(violations)} violation(s) found:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print("PASS")
    print("file-coverage")
    print(
        "every tracked file is covered by a required check or a justified "
        "exclusion, and every declared check is a CI job in the gate"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
