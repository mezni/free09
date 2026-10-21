"""Analytics router — assembles the analytics endpoints into the platform router.

Task T013 places the router here; tasks T014–T016 place the handlers in
`src/api/endpoints/analytics.py`.
"""

from fastapi import APIRouter, status

from src.api.endpoints.analytics import (
    AnalyticsEventCreate,
    AnalyticsEventRead,
    create_analytics_event,
    get_analytics_event,
    list_analytics_events,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

router.add_api_route(
    "/events",
    list_analytics_events,
    methods=["GET"],
    response_model=list[AnalyticsEventRead],
    summary="List analytics events",
)
router.add_api_route(
    "/events/{event_id}",
    get_analytics_event,
    methods=["GET"],
    response_model=AnalyticsEventRead,
    summary="Get an analytics event",
)
router.add_api_route(
    "/events",
    create_analytics_event,
    methods=["POST"],
    response_model=AnalyticsEventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an analytics event",
)

__all__ = [
    "AnalyticsEventCreate",
    "AnalyticsEventRead",
    "router",
]
