"""Noxfile for telco platform — session framework and result reporter.

Exit-code contract (mirrored in `ci/run-checks.sh` and the README):

* 0 — PASS (all checks passed)
* 1 — FAIL (one or more checks failed)
* 2 — COULD NOT RUN (check could not execute)
* 3 — INTERNAL ERROR (unexpected failure)
"""

import subprocess
from pathlib import Path

import nox

REPO_ROOT = Path(__file__).parent
COMPOSE_FILE = "deploy/compose/compose.yaml"

nox.options.default_venv_backend = "uv"


class CommandResult:
    """Reporter for command execution results."""

    PASS = 0
    FAIL = 1
    COULD_NOT_RUN = 2
    INTERNAL_ERROR = 3

    def __init__(self, exit_code: int, output: str = "", error: str = ""):
        self.exit_code = exit_code
        self.output = output
        self.error = error
        self.status = self._status_name(exit_code)

    def _status_name(self, code: int) -> str:
        return {
            self.PASS: "PASS",
            self.FAIL: "FAIL",
            self.COULD_NOT_RUN: "COULD NOT RUN",
            self.INTERNAL_ERROR: "INTERNAL ERROR",
        }.get(code, "UNKNOWN")

    def __bool__(self) -> bool:
        return self.exit_code == self.PASS

    def __str__(self) -> str:
        return f"[{self.status}] exit={self.exit_code}"


def run_session(session_name: str, *args: str, **kwargs) -> CommandResult:
    """Run a nox session and return a structured result.

    Args:
        session_name: Name of the nox session to run.
        *args: Additional arguments to pass to the session.
        **kwargs:
            auto_return: If True, return immediately after running (default False).
            hide_output: If True, hide command output (default False).

    Returns:
        CommandResult with exit code, output, and status.
    """
    kwargs.pop("auto_return", None)
    hide_output = kwargs.pop("hide_output", False)

    cmd = ["nox", "run", session_name, *args]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    output = result.stdout if not hide_output else result.stdout + result.stderr
    return CommandResult(result.returncode, output[:1000], result.stderr[:500])


def run_fast_checks() -> CommandResult:
    """Run the fast-checks nox session."""
    return run_session("fast-checks")


def run_slow_checks() -> CommandResult:
    """Run the slow-checks nox session."""
    return run_session("slow-checks")


def check_health() -> CommandResult:
    """Run the health check session."""
    return run_session("health-check")


def install_deps(session: nox.Session, *extra: str) -> None:
    """Install the project and its development dependency group into the venv."""
    session.install("-e", ".", "--group", "dev")
    if extra:
        session.install(*extra)


# --- Quality sessions ---


@nox.session(reuse_venv=True)
def format(session: nox.Session) -> None:
    """Check formatting with ruff format."""
    install_deps(session)
    session.run("ruff", "format", "--check", ".")


@nox.session(reuse_venv=True)
def lint(session: nox.Session) -> None:
    """Lint the repository with ruff."""
    install_deps(session)
    session.run("ruff", "check", ".")


@nox.session(reuse_venv=True)
def typecheck(session: nox.Session) -> None:
    """Type-check the application packages with mypy."""
    install_deps(session)
    session.run(
        "mypy",
        "src",
        "libs/telco-common/src",
        "--ignore-missing-imports",
        "--no-error-summary",
    )


@nox.session(reuse_venv=True)
def test(session: nox.Session) -> None:
    """Run the fast test suite."""
    install_deps(session)
    session.run("pytest", "tests", "-q", "-m", "not slow and not integration")


@nox.session(reuse_venv=True)
def test_cov(session: nox.Session) -> None:
    """Run the test suite with coverage reporting."""
    install_deps(session)
    session.run("pytest", "tests", "-q", "--cov=src", "--cov-report=term-missing")


@nox.session(reuse_venv=True)
def lockfile(session: nox.Session) -> None:
    """Verify the lockfile is current with respect to pyproject.toml."""
    install_deps(session)
    session.run("uv", "lock", "--check")


@nox.session(reuse_venv=True)
def secret_scan(session: nox.Session) -> None:
    """Scan the tracked tree for committed secrets."""
    install_deps(session)
    session.run("python", "ci/secret_scan.py")


@nox.session(reuse_venv=True)
def dep_audit(session: nox.Session) -> None:
    """Audit locked dependencies for known vulnerabilities."""
    install_deps(session)
    session.run("python", "ci/dependency_audit.py")


@nox.session(reuse_venv=True)
def fast_checks(session: nox.Session) -> None:
    """Run every check required by the local verification lane."""
    install_deps(session)
    session.run("ruff", "format", "--check", ".")
    session.run("ruff", "check", ".")
    session.run("uv", "lock", "--check", external=True)
    session.run(
        "mypy",
        "src",
        "libs/telco-common/src",
        "--ignore-missing-imports",
        "--no-error-summary",
    )
    session.run("pytest", "tests", "-q", "-m", "not slow and not integration")
    session.run("python", "ci/secret_scan.py")
    session.run("python", "ci/dependency_audit.py")


@nox.session(reuse_venv=True)
def slow_checks(session: nox.Session) -> None:
    """Run the integration suite (requires a running service stack)."""
    install_deps(session)
    session.run("pytest", "tests", "-q", "-m", "integration or slow")


@nox.session(reuse_venv=True)
def health_check(session: nox.Session) -> None:
    """Verify the local runtime stack answers health probes."""
    install_deps(session)
    session.run("python", "ci/health_check.py")


# --- Environment sessions ---


@nox.session(reuse_venv=True)
def setup(session: nox.Session) -> None:
    """Initialize the project structure and verify prerequisites."""
    install_deps(session)
    session.run("python", "-c", "import ci.check_prerequisites as p; p.main()")


@nox.session(reuse_venv=True)
def db_up(session: nox.Session) -> None:
    """Start PostgreSQL via docker compose."""
    session.run("docker", "compose", "-f", COMPOSE_FILE, "up", "-d", "postgres")


@nox.session(reuse_venv=True)
def db_down(session: nox.Session) -> None:
    """Stop PostgreSQL via docker compose."""
    session.run("docker", "compose", "-f", COMPOSE_FILE, "down")
