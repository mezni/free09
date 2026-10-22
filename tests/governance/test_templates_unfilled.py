"""Template test — the templates carry unfilled placeholders only.

Test ID: `test_templates_contain_only_placeholders`
"""

import pytest

from tests.governance.helpers import FILLED_IDENTIFIER, PLACEHOLDER, REPO_ROOT, read

pytestmark = pytest.mark.governance

TEMPLATES_DIR = REPO_ROOT / "templates"

REQUIRED_TEMPLATES = (
    "feature-spec-template.md",
    "implementation-plan-template.md",
    "tasks-template.md",
    "adr-template.md",
    "decision-log-template.md",
)


def _templates():
    """Return the templates in the repository."""
    if not TEMPLATES_DIR.is_dir():
        return []
    return sorted(TEMPLATES_DIR.glob("*.md"))


class TestTemplatesUnfilled:
    """Every template is reusable and unfilled."""

    def test_templates_contain_only_placeholders(self):
        """Each template carries placeholders and no resolved identifier."""
        templates = _templates()
        assert templates, "The repository holds no templates."

        for template in templates:
            content = template.read_text(encoding="utf-8")
            assert PLACEHOLDER.search(content), (
                f"{template.name} carries no unfilled placeholder; a template "
                "must be reusable and unfilled."
            )
            filled = FILLED_IDENTIFIER.findall(content)
            assert not filled, (
                f"{template.name} contains the resolved identifier(s) {filled}; a "
                "template must not carry a resolved specification or ADR id."
            )

    def test_the_required_templates_exist(self):
        """Every required document type has a template."""
        names = {template.name for template in _templates()}
        missing = [name for name in REQUIRED_TEMPLATES if name not in names]
        assert not missing, f"The repository is missing these templates: {missing}"

    def test_each_template_declares_its_sections(self):
        """Each template declares at least two sections for its document type."""
        for template in _templates():
            content = template.read_text(encoding="utf-8")
            headings = [line for line in content.splitlines() if line.startswith("## ")]
            assert len(headings) >= 2, (
                f"{template.name} declares fewer than two sections; it does not "
                "describe a document structure."
            )

    def test_the_tasks_template_describes_the_task_format(self):
        """The tasks template states the task format the repository uses."""
        content = read("templates/tasks-template.md")
        assert "[ID] [P?] [Story] Description" in content, (
            "The tasks template does not state the task format."
        )
        assert "- [ ] T001" in content, (
            "The tasks template carries no example task in the repository's format."
        )
