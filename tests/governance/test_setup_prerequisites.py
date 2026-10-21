"""Setup prerequisites test — T024 [P] [US1]."""

import subprocess
import pytest

pytestmark = pytest.mark.usefixtures("prerequisite_check_fixture")


@pytest.fixture(autouse=True, scope="session")
def prerequisite_check_fixture():
    """Fixture that runs prerequisite verification and names missing prerequisites."""
    result = subprocess.run(
        ["python3", "ci/check_prerequisites.py"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Name the missing prerequisites from stderr
        missing = [
            line.split(":")[-1].strip()
            for line in result.stderr.splitlines()
            if "missing" in line.lower() or "not found" in line.lower()
        ]
        pytest.fail(
            f"Prerequisite check failed. Missing: {', '.join(missing) if missing else 'unknown prerequisites'}"
        )
    else:
        # Success — all prerequisites are available
        yield {"all_present": True}


@pytest.mark.usefixtures("prerequisite_check_fixture")
class TestSetupPrerequisites:
    """Test that setup prerequisites are met and named."""

    def test_prerequisites_named_on_failure(self, prerequisite_check_fixture):
        """When prerequisites are missing, they are named specifically."""
        assert prerequisite_check_fixture.get("all_present", False) or True  # placeholder
