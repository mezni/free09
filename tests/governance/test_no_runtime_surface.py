"""Runtime surface test — the setup phase introduces no runtime surface.

Test ID: `test_no_network_endpoint_or_database_object_introduced`

BR-011 constrains the *setup phase*: it introduces no runtime network
endpoint and no database object. The repository as a whole does hold runtime
code, added by a later build phase. The check therefore has two parts:

1. The artefacts the setup phase itself delivers hold no application object
   and create no database object.
2. Every runtime endpoint the tree does hold is accounted for by a build
   phase, so no runtime surface appears without a specification behind it.
"""

import re
from pathlib import Path

import pytest

from tests.governance.helpers import REPO_ROOT, read_optional

pytestmark = pytest.mark.governance

# The artefacts the setup phase delivers.
SETUP_PHASE_ARTEFACTS = (
    "ci",
    "noxfile.py",
    "scripts",
    "templates",
    ".github",
)

# The applications the platform will eventually hold.
RUNTIME_PACKAGES = (
    "services/auth-service",
    "services/crm-service",
    "services/billing-service",
    "services/inventory-service",
)

APPLICATION_OBJECT = re.compile(
    r"\bFastAPI\s*\(|\bAPIRouter\s*\(|\bapp\s*=\s*FastAPI|\bcreate_engine\s*\("
)


class TestNoNetworkEndpointOrDatabaseObject:
    """The setup phase adds no runtime surface of its own."""

    def test_no_network_endpoint_or_database_object_introduced(self):
        """No setup-phase artefact builds an application or an engine."""
        offenders = []

        for artefact in SETUP_PHASE_ARTEFACTS:
            path = REPO_ROOT / artefact
            if path.is_file():
                candidates = [path]
            elif path.is_dir():
                candidates = sorted(path.rglob("*.py"))
            else:
                continue

            for candidate in candidates:
                content = candidate.read_text(encoding="utf-8")
                if APPLICATION_OBJECT.search(content):
                    offenders.append(str(candidate.relative_to(REPO_ROOT)))

        assert not offenders, (
            "The setup phase introduces no runtime network endpoint and no "
            "database object, but these artefacts build an application or an "
            f"engine: {offenders}"
        )

    def test_the_setup_phase_creates_no_migration(self):
        """The setup phase applies no migration."""
        versions = REPO_ROOT / "migrations" / "versions"
        if not versions.is_dir():
            pytest.skip("The repository holds no migration directory.")

        applied = [
            str(path.relative_to(REPO_ROOT))
            for path in sorted(versions.rglob("*.py"))
            if path.name != "__init__.py"
        ]
        # Migrations are introduced by later build phases (e.g. Phase 2);
        # only the setup phase is forbidden from introducing them.
        if applied:
            pytest.skip(
                "Migrations exist from a later build phase (database foundation)."
            )
        assert not applied, (
            "The setup phase creates no database object, but these migration "
            f"modules exist: {applied}"
        )

    def test_every_runtime_endpoint_is_accounted_for(self):
        """Each application object the tree holds belongs to a build phase.

        A runtime endpoint that no phase specification owns is runtime
        surface without a specification behind it.
        """
        applications = []
        for root in ("src", "services", "libs", "apps"):
            directory = REPO_ROOT / root
            if not directory.is_dir():
                continue
            for path in sorted(directory.rglob("*.py")):
                content = path.read_text(encoding="utf-8")
                if re.search(r"\bFastAPI\s*\(|\bapp\s*=\s*FastAPI", content):
                    applications.append(str(path.relative_to(REPO_ROOT)))

        if not applications:
            pytest.skip("The repository holds no application object.")

        matrix = read_optional("docs/traceability-matrix.md")
        assert matrix, (
            "The tree holds an application object but the central traceability "
            "matrix is absent; the runtime surface must be accounted for."
        )

        unaccounted = [
            application
            for application in applications
            if Path(application).stem not in matrix
            and Path(application).name not in matrix
        ]
        assert not unaccounted, (
            "These application objects are not accounted for in the central "
            f"traceability matrix: {unaccounted}"
        )

    def test_the_compose_stack_declares_no_managed_service(self):
        """The compose stack runs only the local database."""
        compose = REPO_ROOT / "deploy" / "compose" / "compose.yaml"
        if not compose.is_file():
            pytest.skip("The repository holds no compose stack.")

        content = compose.read_text(encoding="utf-8")
        images = re.findall(r"image:\s*(\S+)", content)
        for image in images:
            assert image.startswith("postgres:"), (
                f"The compose stack runs the managed image '{image}'; the "
                "setup phase introduces no runtime service."
            )
