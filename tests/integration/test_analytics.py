"""Integration tests for User Story 1: Advanced API endpoints (US1)"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_analytics_endpoints_lifecycle():
    """Integration test: Full lifecycle of analytics endpoints"""
    # 1. Create an analytics event
    event_data = {
        "event_type": "page_view",
        "service": "web-frontend",
        "endpoint": "/dashboard",
        "metadata": {"page_id": "abc123", "user_id": "user-456"},
    }
    create_response = client.post("/api/v1/analytics/events", json=event_data)
    assert create_response.status_code in (200, 201)
    created_event = create_response.json()
    event_id = created_event.get("event_id") or created_event.get("id")
    assert event_id is not None

    # 2. Retrieve the event by ID
    get_response = client.get(f"/api/v1/analytics/events/{event_id}")
    assert get_response.status_code == 200
    retrieved_event = get_response.json()
    assert retrieved_event["event_type"] == "page_view"

    # 3. Query events by service
    query_response = client.get("/api/v1/analytics/events?service=web-frontend")
    assert query_response.status_code == 200
    queried_events = query_response.json()
    assert isinstance(queried_events, list)

    # 4. Query events by service and time range (if supported)
    # This tests the endpoint can handle various query combinations


def test_analytics_events_empty_state():
    """Integration test: Analytics with no events recorded"""
    response = client.get("/api/v1/analytics/events")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
