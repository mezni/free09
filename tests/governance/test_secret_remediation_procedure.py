"""Secret-remediation test — the repository states a remediation procedure.

Test ID: `test_secret_remediation_procedure_is_documented`
"""

import pytest

from tests.governance.helpers import read, read_optional

pytestmark = pytest.mark.governance

CANDIDATES = (
    "CONTRIBUTING.md",
    "docs/quality/development-workflow.md",
    "docs/governance/precedence-and-conventions.md",
    "specs/001-project-setup/research.md",
)

# The steps a remediation runbook must name.
REQUIRED_STEPS = (
    "rotate",
    "revoke",
)


class TestSecretRemediationProcedure:
    """A committed secret has a documented remediation path."""

    def test_secret_remediation_procedure_exists(self):
        """A remediation runbook exists and names its steps."""
        documents = {
            path: content
            for path in CANDIDATES
            if (content := read_optional(path)) is not None
        }
        assert documents, (
            "The repository documents no remediation path for committed secret "
            f"material. Looked in: {list(CANDIDATES)}"
        )

        combined = "\n".join(documents.values()).lower()
        for step in REQUIRED_STEPS:
            assert step in combined, (
                f"The remediation procedure does not mention '{step}'; a "
                "remediation that does not revoke or rotate the credential "
                "leaves it usable."
            )

        assert "git-filter-repo" in combined or "filter-repo" in combined, (
            "The remediation procedure does not name the history-rewrite tool."
        )

    def test_the_remediation_procedure_states_the_order(self):
        """The runbook states that revocation comes before the rewrite."""
        content = read("CONTRIBUTING.md")
        lower = content.lower()

        rotate_index = lower.find("rotat")
        rewrite_index = lower.find("filter-repo")
        assert rotate_index != -1, (
            "CONTRIBUTING.md states neither the rotation step nor the "
            "history-rewrite step."
        )
        assert rewrite_index != -1, (
            "CONTRIBUTING.md states neither the rotation step nor the "
            "history-rewrite step."
        )
        assert rotate_index < rewrite_index, (
            "CONTRIBUTING.md presents the history rewrite before the rotation; "
            "the credential must be revoked or rotated first."
        )

    def test_the_remediation_procedure_names_a_verification_step(self):
        """The runbook says how the remediation is verified."""
        content = read("CONTRIBUTING.md").lower()
        assert "secret_scan" in content or "secret scan" in content, (
            "CONTRIBUTING.md does not name the scan that verifies the remediation."
        )
