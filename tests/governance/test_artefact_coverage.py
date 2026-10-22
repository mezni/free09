"""Artefact coverage test — every declared artefact has a check that owns it.

Test ID: `test_every_declared_artefact_is_owned_by_a_check`
"""

import pytest

from tests.governance.helpers import read, tracked_files

pytestmark = pytest.mark.governance

FILE_COVERAGE = "ci/file-coverage.yml"


class TestArtefactCoverage:
    """Every tracked artefact is owned by a required check."""

    def test_every_phase_artifact_covered_by_gate_or_exemption(self):
        """No tracked file escapes the coverage declaration."""
        content = read(FILE_COVERAGE)

        globs = _declared_globs(content)
        exclusions = _declared_exclusions(content)
        assert globs, f"{FILE_COVERAGE} declares no coverage glob."

        unowned = []
        for path in tracked_files():
            if _matches(path, globs):
                continue
            if _matches(path, exclusions):
                continue
            unowned.append(path)

        assert not unowned, (
            "These tracked files are neither covered by a required check nor "
            f"excluded with a reason: {unowned}"
        )

    def test_every_exclusion_names_an_owner_and_a_review_date(self):
        """An exclusion states why, who owns it, and when it is reviewed."""
        content = read(FILE_COVERAGE)
        blocks = content.split("  - paths:")[1:]

        assert blocks, f"{FILE_COVERAGE} declares no exclusion."

        for block in blocks:
            for field in ("reason:", "owner:", "review_by:"):
                assert field in block, (
                    f"{FILE_COVERAGE} has an exclusion with no '{field}'"
                )

    def test_the_coverage_declaration_names_the_required_checks(self):
        """Every required check appears in the coverage declaration."""
        from tests.governance.helpers import REQUIRED_CHECKS

        content = read(FILE_COVERAGE)
        for check in REQUIRED_CHECKS:
            assert f"\n  {check}:" in content, (
                f"{FILE_COVERAGE} declares no coverage for the '{check}' check."
            )

    def test_the_coverage_check_itself_is_covered(self):
        """The coverage declaration is owned by the coverage check."""
        content = read(FILE_COVERAGE)
        assert "ci/file-coverage.yml" in content, (
            f"{FILE_COVERAGE} does not cover itself."
        )
        assert "ci/check_file_coverage.py" in content, (
            f"{FILE_COVERAGE} does not cover the check that reads it."
        )


def _declared_globs(content: str) -> list[str]:
    """Return the coverage globs the declaration carries."""
    globs: list[str] = []
    in_covers = False

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.endswith(":") and not stripped.startswith("-"):
            in_covers = stripped == "covers:"
            continue
        if in_covers and stripped.startswith("- "):
            globs.append(stripped[2:].strip().strip('"').strip("'"))

    return globs


def _declared_exclusions(content: str) -> list[str]:
    """Return the exclusion globs the declaration carries."""
    globs: list[str] = []
    in_paths = False

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.endswith(":"):
            in_paths = stripped == "paths:"
            continue
        if in_paths and stripped.startswith("- "):
            globs.append(stripped[2:].strip().strip('"').strip("'"))

    return globs


def _matches(path: str, globs: list[str]) -> bool:
    """Return whether a path matches any of the globs."""
    import fnmatch

    for glob in globs:
        if fnmatch.fnmatch(path, glob):
            return True
        if glob.startswith("**/") and fnmatch.fnmatch(path, glob[3:]):
            return True
        if fnmatch.fnmatch(path, f"{glob.rstrip('/')}/**"):
            return True
    return False
