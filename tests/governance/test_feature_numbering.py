"""Feature numbering test — the feature directories are numbered and complete.

Test ID: `test_feature_directories_are_numbered_and_complete`
"""

import pytest

from tests.governance.helpers import FEATURE_DIR, feature_directories

pytestmark = pytest.mark.governance

REQUIRED_ARTEFACTS = (
    "spec.md",
    "tasks.md",
    "checklists/requirements.md",
)


class TestFeatureNumbering:
    """Every feature is numbered once and carries its artefacts."""

    def test_feature_directories_are_numbered_and_complete(self):
        """Feature directories are uniquely numbered and hold their artefacts."""
        directories = feature_directories()
        assert directories, "The repository holds no feature directories."

        numbers = []
        for directory in directories:
            match = FEATURE_DIR.match(directory.name)
            assert match is not None, (
                f"'{directory.name}' does not follow the naming convention "
                "<nnn>-<kebab-case-name>."
            )
            numbers.append(int(match.group(1)))

        assert len(numbers) == len(set(numbers)), (
            "Two feature directories share a number."
        )
        assert sorted(numbers) == list(range(1, len(numbers) + 1)), (
            f"The feature numbers are not sequential: {sorted(numbers)}"
        )

        for directory in directories:
            for artefact in REQUIRED_ARTEFACTS:
                assert (directory / artefact).is_file(), (
                    f"'{directory.name}' does not hold '{artefact}'."
                )

    def test_every_feature_directory_is_numbered(self):
        """No directory under specs/ escapes the naming convention."""
        from tests.governance.helpers import REPO_ROOT

        specs_dir = REPO_ROOT / "specs"
        unnamed = [
            entry.name
            for entry in specs_dir.iterdir()
            if entry.is_dir() and not FEATURE_DIR.match(entry.name)
        ]
        assert not unnamed, (
            f"These directories under specs/ are not numbered features: {unnamed}"
        )
