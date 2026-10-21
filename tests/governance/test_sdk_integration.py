"""SDK integration tests — T082 [P] [US2]."""


import pytest
import requests


@pytest.mark.usefixtures("running_services")
class TestSDKIntegration:
    """Integration tests for SDK methods against running services."""

    @pytest.fixture(autouse=True)
    def running_services(self):
        """Ensure services are running for integration tests."""
        import subprocess
        result = subprocess.run(
            ["docker", "compose", "-f", "deploy/compose/compose.yaml", "up", "-d", "postgres"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        import time
        time.sleep(5)  # Wait for services to be ready
        yield
        # Teardown
        subprocess.run(
            ["docker", "compose", "-f", "deploy/compose/compose.yaml", "down"],
            capture_output=True,
        )

    def test_person_create_via_sdk(self, running_services):
        """Test person creation via the Python SDK."""
        from services.auth_service.sdk.person_api import PersonApiClient

        client = PersonApiClient(
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

    def test_person_get_via_sdk(self, running_services):
        """Test person retrieval via the Python SDK."""
        from services.auth_service.sdk.person_api import PersonApiClient

        client = PersonApiClient(
            base_url="http://localhost:8000",
            auth_header={"Authorization": "Bearer test-jwt-token"},
        )

        # First create a person
        created = client.create_person(
            name="Test User", email="test@example.com"
        )

        # Then retrieve it
        retrieved = client.get_person(created["id"])

        assert retrieved["name"] == "Test User"
        assert retrieved["email"] == "test@example.com"
        assert retrieved["id"] == created["id"]
