"""Template content test — no template carries approved content.

Test ID: `test_templates_do_not_carry_approved_content`
"""

import re

import pytest

from tests.governance.helpers import REPO_ROOT, feature_directories

pytestmark = pytest.mark.governance

TEMPLATES_DIR = REPO_ROOT / "templates"

# Values that belong to a specific feature, and therefore to no template.
FEATURE_SPECIFIC = (
    "auth-service",
    "crm-service",
    "billing-service",
    "inventory-service",
    "telco_platform",
    "telco-platform",
)


def _templates():
    """Return the templates in the repository."""
    if not TEMPLATES_DIR.is_dir():
        return []
    return sorted(TEMPLATES_DIR.glob("*.md"))


class TestTemplatesNoApprovedContent:
    """A template belongs to no feature in particular."""

    def test_templates_do_not_carry_approved_content(self):
        """No template names a feature, a decided value, or an approved status."""
        templates = _templates()
        assert templates, "The repository holds no templates."

        for template in templates:
            content = template.read_text(encoding="utf-8")
            name = template.name

            for value in FEATURE_SPECIFIC:
                assert value not in content, (
                    f"{name} names '{value}', which belongs to a specific "
                    "feature; a template must carry no approved content."
                )

            for decision in re.findall(r"^- Status:\s*(.+)$", content, re.MULTILINE):
                assert "Proposed /" in decision or "/" in decision, (
                    f"{name} states the status '{decision}' as if it were decided."
                )

    def test_no_template_reproduces_a_real_feature_name(self):
        """No template carries the name of a feature directory in the tree."""
        names = {directory.name for directory in feature_directories()}
        for template in _templates():
            content = template.read_text(encoding="utf-8")
            for name in sorted(names):
                assert name not in content, (
                    f"{template.name} carries the real feature directory name '{name}'."
                )

    def test_no_template_carries_a_real_decision_value(self):
        """No template carries a value that a decision record has fixed."""
        for template in _templates():
            content = template.read_text(encoding="utf-8")
            assert "postgres:16" not in content, (
                f"{template.name} carries the decided database image tag."
            )
            assert "uv lock" not in content, (
                f"{template.name} carries a decided toolchain command."
            )
