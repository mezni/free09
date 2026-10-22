"""Offline test — the required checks run without network access.

Test ID: `test_checks_complete_without_network_access`
"""

import re

import pytest

from tests.governance.helpers import REQUIRED_CHECKS, WORKFLOW, read

pytestmark = pytest.mark.governance

# Modules that make outbound requests.
NETWORK_MODULES = ("requests", "httpx", "urllib.request", "aiohttp", "socket")

# The required-check scripts, by the session that runs them.
CHECK_SCRIPTS = (
    "ci/check_spec_artifacts.py",
    "ci/check_file_coverage.py",
    "ci/check_dependencies.py",
    "ci/secret_scan.py",
)


class TestChecksOffline:
    """The required checks do not depend on the network."""

    def test_checks_complete_without_network_access(self):
        """No required check imports a network client or downloads anything."""
        for script in CHECK_SCRIPTS:
            content = read(script)
            for module in NETWORK_MODULES:
                assert f"import {module}" not in content, (
                    f"{script} imports '{module}'; a required check must not "
                    "depend on the network."
                )

    def test_dependency_audit_uses_the_vendored_snapshot(self):
        """The dependency audit reads the vendored snapshot, not an API."""
        content = read("ci/check_dependencies.py")
        assert "ci/advisories/python-advisories.json" in content, (
            "The dependency audit does not read the vendored advisory snapshot."
        )
        assert "pip-audit" not in content, (
            "The dependency audit invokes pip-audit, which needs the network."
        )

    def test_lockfile_check_resolves_offline(self):
        """The lockfile check resolves without reaching the index."""
        content = read("noxfile.py")
        lockfile = re.search(r"def lockfile\(.*?\n(?P<body>(?:    .*\n|\n)*)", content)
        assert lockfile is not None, "noxfile.py has no lockfile session."
        assert "uv" in lockfile.group("body"), "The lockfile session does not run uv."
        assert "lock" in lockfile.group("body"), (
            "The lockfile session does not check the lockfile."
        )

    def test_workflow_downloads_nothing_at_check_time(self):
        """The workflow does not fetch anything while a check runs."""
        workflow = read(WORKFLOW)
        for command in ("curl", "wget", "pip install", "pip download"):
            assert command not in workflow, (
                f"The workflow downloads with '{command}'; the required checks "
                "must run from the committed lockfile."
            )

    def test_every_required_check_has_a_definition_site(self):
        """Every required check is defined in the noxfile, not only in CI."""
        noxfile = read("noxfile.py")
        for check in REQUIRED_CHECKS:
            assert f'"{check}"' in noxfile, (
                f"noxfile.py does not define the '{check}' session."
            )
