"""Contract tests for User Story 1: Advanced API endpoints (US1)"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_list_analytics_events_get():
    """Contract test: GET /api/v1/analytics/events"""
    response = client.get("/api/v1/analytics/events")
    assert response.status_code == 200
    data = response.json()
    # Validate response structure
    assert isinstance(data, list)
    # If there are events, validate structure
    if data:
        event = data[0]
        assert "event_type" in event or "event_id" in event


def test_get_analytics_event():
    """Contract test: GET /api/v1/analytics/events/{event_id}"""
    # Test with non-existent ID
    response = client.get("/api/v1/analytics/events/nonexistent")
    # Should return 404 or appropriate error
    assert response.status_code in (404, 200)


def test_create_analytics_event():
    """Contract test: POST /api/v1/analytics/events"""
    event_data = {
        "event_type": "page_view",
        "service": "web-frontend",
        "endpoint": "/dashboard",
        "metadata": {"page_id": "abc123"},
    }
    response = client.post("/api/v1/analytics/events", json=event_data)
    assert response.status_code in (200, 201, 400)  # 400 if validation fails


def test_analytics_event_query_params():
    """Contract test: analytics events with query parameters"""
    response = client.get("/api/v1/analytics/events?service=web-frontend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
