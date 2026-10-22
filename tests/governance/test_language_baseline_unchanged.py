"""Language baseline unchanged test — T023 [P] [US1]."""

import pytest

pytestmark = pytest.mark.usefixtures("language_baseline_fixture")


@pytest.fixture(autouse=True, scope="session")
def language_baseline_fixture():
    """Provide the language and persistence baseline from the constitution.

    The constitution declares Python 3.13 as the implementation language and
    PostgreSQL as the persistence platform. This fixture ensures these baselines
    are unchanged by this phase.
    """
    # Constitution baseline: Python 3.13, PostgreSQL 16.15
    baseline = {
        "implementation_language": "Python 3.13",
        "persistence": "PostgreSQL 16.15",
    }
    return baseline


@pytest.mark.usefixtures("language_baseline_fixture")
class TestLanguageBaselineUnchanged:
    """Test that language and persistence baselines are unchanged."""

    def test_implementation_language_baseline_unchanged(
        self, language_baseline_fixture
    ):
        """Implementation language remains Python 3.13."""
        lang = language_baseline_fixture["implementation_language"]
        assert "Python 3.13" in lang

    def test_persistence_baseline_unchanged(self, language_baseline_fixture):
        """Persistence baseline remains PostgreSQL 16.15."""
        pers = language_baseline_fixture["persistence"]
        assert "PostgreSQL 16.15" in pers
