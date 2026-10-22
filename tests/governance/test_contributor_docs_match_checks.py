"""Contributor documentation test — the guide covers the checks and obligations.

Test ID: `test_contributor_docs_cover_setup_checks_and_obligations`
"""

import pytest

from tests.governance.helpers import REQUIRED_CHECKS, read

pytestmark = pytest.mark.governance


class TestContributorDocs:
    """The contributor guide covers the setup path, the checks, and the rules."""

    def test_contributor_docs_cover_setup_checks_and_obligations(self):
        """The guide names the setup path, every required check, and the rules."""
        guide = read("CONTRIBUTING.md")

        assert "make setup" in guide, "The guide does not name the setup command."
        assert "make verify" in guide, "The guide does not name the verify command."

        missing = [check for check in REQUIRED_CHECKS if check not in guide]
        assert not missing, (
            f"The contributor guide does not mention these required checks: {missing}"
        )

        for obligation in (
            "Documentation",
            "Approval",
            "exception",
            "rationale",
            "risk",
            "scope",
            "owner",
            "compensating controls",
            "review date",
        ):
            assert obligation.lower() in guide.lower(), (
                f"The contribution rules do not cover '{obligation}'."
            )

    def test_guide_states_the_exception_route(self):
        """The guide states when an exception is acceptable and what it needs."""
        guide = read("CONTRIBUTING.md")
        for field in (
            "rationale",
            "risk",
            "scope",
            "owner",
            "compensating control",
            "review date",
        ):
            assert field in guide.lower(), (
                f"The exception route does not require a '{field}'."
            )
