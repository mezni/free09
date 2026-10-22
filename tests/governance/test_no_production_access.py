"""Production-access test — no production system is reachable from the tree.

Test ID: `test_no_production_access_in_the_tree`
"""

import re
import subprocess
from pathlib import Path

import pytest

from tests.governance.helpers import REPO_ROOT

pytestmark = pytest.mark.governance

# A host that must never appear in a tracked configuration.
PRODUCTION_HOSTS = (
    "prod.telco",
    "production.telco",
    "rds.amazonaws.com",
    "azure.com",
)

# The one tracked file that must name the hosts it searches for.
SCANNER_FILE = Path(__file__).resolve().relative_to(REPO_ROOT).as_posix()

# The placeholder literals the repository documents. `ci/secret_scan.py` and
# `.gitleaks.toml` treat them as placeholders; this test must agree.
PLACEHOLDER_LITERALS = (
    "placeholder_no_real_credential",
    "password_placeholder",
    "localdevpassword",
    "test-jwt-token",
)


def _tracked_files() -> list[str]:
    """Return the paths of the tracked files."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _is_placeholder(value: str) -> bool:
    """Return whether a value is one of the documented placeholders."""
    lowered = value.lower()
    if "placeholder" in lowered:
        return True
    return lowered in PLACEHOLDER_LITERALS


class TestNoProductionAccess:
    """The repository reaches no production system."""

    def test_setup_requires_no_production_access(self):
        """No tracked file names a production host.

        This file is the single exception: it holds the patterns it searches
        for, so it cannot be scanned for them.
        """
        offenders = []
        for path in _tracked_files():
            if path == SCANNER_FILE:
                continue
            target = REPO_ROOT / path
            try:
                content = target.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            lowered = content.lower()
            for host in PRODUCTION_HOSTS:
                if host in lowered:
                    offenders.append(f"{path}: {host}")

        assert not offenders, f"These tracked files name a production host: {offenders}"

    def test_no_production_credential_is_configured(self):
        """No tracked file holds a usable credential."""
        offenders = []
        for path in _tracked_files():
            if not path.endswith((".env", ".yml", ".yaml", ".toml", ".json", ".ini")):
                continue
            target = REPO_ROOT / path
            try:
                content = target.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for match in re.finditer(
                r"(?i)(password|secret|token|api_key)\s*[:=]\s*[\"']?([^\s\"'#]+)",
                content,
            ):
                value = match.group(2)
                if _is_placeholder(value):
                    continue
                if value.lower() in {"", "none", "null", "changeme"}:
                    continue
                if value.startswith("${") or value.startswith("$"):
                    continue
                offenders.append(f"{path}: {match.group(1)}")

        assert not offenders, (
            f"These tracked files hold a usable credential: {offenders}"
        )

    def test_the_compose_stack_reaches_no_external_host(self):
        """Every connection string in the compose stack names its own service."""
        compose = REPO_ROOT / "deploy" / "compose" / "compose.yaml"
        if not compose.is_file():
            pytest.skip("The repository holds no compose stack.")

        content = compose.read_text(encoding="utf-8")
        services = set(re.findall(r"^  ([a-z0-9-]+):$", content, re.MULTILINE))
        assert services, "The compose stack declares no service."

        hosts = set()
        for match in re.finditer(
            r"://[^:/@\s]+(?::[^@\s]*)?@([A-Za-z0-9_.-]+)", content
        ):
            hosts.add(match.group(1))
        for match in re.finditer(r"(?m)^\s+POSTGRES_HOST:\s*(\S+)", content):
            hosts.add(match.group(1))

        external = sorted(host for host in hosts if host not in services)
        assert not external, (
            f"The compose stack connects to a host it does not define: {external}"
        )

    def test_the_compose_stack_publishes_only_to_the_local_host(self):
        """The published port binds to the loopback interface."""
        compose = REPO_ROOT / "deploy" / "compose" / "compose.yaml"
        if not compose.is_file():
            pytest.skip("The repository holds no compose stack.")

        content = compose.read_text(encoding="utf-8")
        published = re.findall(r'-\s+"([\d.]+)?:?(\d+):(\d+)"', content)
        assert published, "The compose stack publishes no port."

        for host, published_port, _container_port in published:
            assert host in {"127.0.0.1", "localhost"}, (
                f"The compose stack publishes port {published_port} on all "
                f"interfaces; bind it to 127.0.0.1 instead."
            )
