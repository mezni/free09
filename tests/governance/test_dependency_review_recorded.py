"""Dependency review test — the dependency review is recorded.

Test ID: `test_dependency_review_is_recorded`
"""

import re

import pytest

from tests.governance.helpers import REPO_ROOT, read, read_optional

pytestmark = pytest.mark.governance

DEPENDABOT = ".github/dependabot.yml"
ADVISORY_SNAPSHOT = "ci/advisories/python-advisories.json"


def _third_party_packages(lock: str) -> set[str]:
    """Return the third-party packages the lockfile pins.

    A workspace member is installed from a local directory, so it is not a
    dependency to audit.
    """
    packages: set[str] = set()

    for block in lock.split("[[package]]")[1:]:
        name = re.search(r'name = "([^"]+)"', block)
        if not name:
            continue
        source = re.search(r"source = \{([^}]*)\}", block)
        source_text = source.group(1) if source else ""
        if "editable" in source_text or "virtual" in source_text:
            continue
        if "registry" not in source_text and "index" not in source_text:
            continue
        packages.add(name.group(1))

    return packages


class TestDependencyReviewRecorded:
    """The repository records how its dependencies are reviewed."""

    def test_dependency_review_recorded(self):
        """The dependency review is configured and its state is recorded."""
        dependabot = read_optional(DEPENDABOT)
        assert dependabot, (
            f"The repository has no {DEPENDABOT}; a dependency review needs a "
            "source of updates."
        )
        assert "package-ecosystem" in dependabot, (
            f"{DEPENDABOT} declares no package ecosystem."
        )
        assert "github-actions" in dependabot, (
            f"{DEPENDABOT} does not track GitHub Actions updates."
        )

        # The advisory snapshot is the recorded state of the audit.
        snapshot = read_optional(ADVISORY_SNAPSHOT)
        assert snapshot, (
            f"The repository has no {ADVISORY_SNAPSHOT}; the dependency audit "
            "has no recorded state."
        )

        content = snapshot.lower()
        for field in ("packages", "advisories"):
            assert field in content, f"{ADVISORY_SNAPSHOT} records no '{field}'."

    def test_the_snapshot_matches_the_lockfile(self):
        """The advisory snapshot covers the packages the lockfile pins."""
        import json

        snapshot = json.loads(read(ADVISORY_SNAPSHOT))
        packages = snapshot.get("packages")
        assert isinstance(packages, (list, dict)), (
            f"{ADVISORY_SNAPSHOT} records no package list."
        )
        assert packages, f"{ADVISORY_SNAPSHOT} records no package."

        lock = read("uv.lock")
        locked = _third_party_packages(lock)
        assert locked, "The lockfile pins no third-party package."

        recorded = set(packages) if isinstance(packages, dict) else set(packages)
        missing = sorted(locked - recorded)
        assert not missing, (
            f"These locked packages are absent from the advisory snapshot: {missing}"
        )

    def test_the_refresh_workflow_keeps_the_snapshot_current(self):
        """A workflow refreshes the advisory snapshot."""
        workflow = read_optional(".github/workflows/refresh-advisories.yml")
        assert workflow, (
            "The repository has no refresh workflow; the advisory snapshot "
            "would go stale silently."
        )
        assert ADVISORY_SNAPSHOT in workflow, (
            "The refresh workflow does not write the advisory snapshot."
        )

    def test_no_dependency_is_pinned_to_a_non_final_release(self):
        """The lockfile may keep OpenTelemetry's experimental beta track.

        OpenTelemetry publishes the stable SDK alongside experimental 0.x
        beta companion packages and pins them exactly. Those packages are
        exempt; every other dependency must be a final release.
        """
        lock = read("uv.lock")
        pre_releases = re.findall(
            r'name = "([^"]+)"\nversion = "([^"]*(?:a|b|rc|dev)\d*)"', lock
        )
        unapproved = [
            (name, version)
            for name, version in pre_releases
            if not name.startswith("opentelemetry-")
        ]
        assert not unapproved, f"The lockfile pins pre-release versions: {unapproved}"

    def test_the_dependency_audit_check_is_offline(self):
        """The required dependency audit runs without a network."""
        script = REPO_ROOT / "ci" / "check_dependencies.py"
        assert script.is_file(), "The repository has no dependency audit script."
        content = script.read_text(encoding="utf-8")
        reaches_network = "urllib" in content or "requests" in content
        assert not reaches_network, (
            "The dependency audit reaches the network; it must read the "
            "recorded snapshot instead."
        )
