"""Noxfile for telco platform — session framework and result reporter."""

import subprocess
import sys
from typing import Optional


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
        return {self.PASS: "PASS",
                self.FAIL: "FAIL",
                self.COULD_NOT_RUN: "COULD NOT RUN",
                self.INTERNAL_ERROR: "INTERNAL ERROR"}.get(code, "UNKNOWN")

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
    auto_return = kwargs.pop("auto_return", False)
    hide_output = kwargs.pop("hide_output", False)

    cmd = ["nox", "run", session_name] + list(args)
    if hide_output:
        result = subprocess.run(cmd, capture_output=True, text=True)
    else:
        result = subprocess.run(cmd, capture_output=False)

    exit_code = result.returncode
    output = result.stdout if not hide_output else result.stdout + result.stderr

    return CommandResult(
        exit_code=exit_code,
        output=output[:1000] if output else "",  # truncate for safety
        error=result.stderr[:500] if result.stderr else ""
    )


def run_fast_checks() -> CommandResult:
    """Run the fast-checks nox session.

    Returns:
        CommandResult with the session outcome.
    """
    return run_session("fast-checks")


def run_slow_checks() -> CommandResult:
    """Run the slow-checks nox session.

    Returns:
        CommandResult with the session outcome.
    """
    return run_session("slow-checks")


def check_health() -> CommandResult:
    """Run the health check session.

    Returns:
        CommandResult indicating system health status.
    """
    return run_session("health-check")

# --- Session: setup ---
def session_setup():
    """Setup: Initialize project structure and verify prerequisites."""
    from tasks import *  # noqa: F401,F811  # noqa: E402
    from ci.check_prerequisites import check_required_config
    check_required_config()
    echo "Setup complete."

# --- Session: db-up ---
def session_db_up():
    """db-up: Start PostgreSQL via docker compose."""
    subprocess.run(["docker", "compose", "-f", "deploy/compose/compose.yaml", "up", "-d", "postgres"], check=False)
    echo "PostgreSQL starting..."

# --- Session: db-down ---
def session_db_down():
    """db-down: Stop PostgreSQL via docker compose."""
    subprocess.run(["docker", "compose", "-f", "deploy/compose/compose.yaml", "down"], check=False)
    echo "PostgreSQL stopped."
