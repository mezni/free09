"""SDK integration tests — T082 [P] [US2]."""

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
    pytest.mark.usefixtures("running_services"),
]


@pytest.fixture(autouse=True)
def running_services(service_reachable_fixture):
    """Ensure a running API is available, otherwise skip the test."""
    if not service_reachable_fixture():
        pytest.skip(
            "Local API is not reachable on http://localhost:8000 — "
            "start the service stack before running SDK integration tests."
        )
    return


def _person_api_client():
    """Import the SDK client, skipping when the SDK package is not importable."""
    try:
        from services.auth_service.sdk.person_api import PersonApiClient
    except ImportError as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"PersonApiClient SDK is not importable: {exc}")
    return PersonApiClient


class TestSDKIntegration:
    """Integration tests for SDK methods against running services."""

    def test_person_create_via_sdk(self):
        """Test person creation via the Python SDK."""
        person_api = _person_api_client()

        client = person_api(
            base_url="http://localhost:8000",
            auth_header={"Authorization": "Bearer test-jwt-token"},
        )

        person = client.create_person(
            name="Jane Doe", email="jane@example.com", phone="+1234567890"
        )

        assert person["name"] == "Jane Doe"
        assert person["email"] == "jane@example.com"
        assert person["phone"] == "+1234567890"
        assert "id" in person

    def test_person_get_via_sdk(self):
        """Test person retrieval via the Python SDK."""
        person_api = _person_api_client()

        client = person_api(
            base_url="http://localhost:8000",
            auth_header={"Authorization": "Bearer test-jwt-token"},
        )

        created = client.create_person(name="Test User", email="test@example.com")
        retrieved = client.get_person(created["id"])

        assert retrieved["name"] == "Test User"
        assert retrieved["email"] == "test@example.com"
        assert retrieved["id"] == created["id"]
