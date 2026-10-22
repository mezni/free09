"""Analytics endpoints — advanced analytics API surface (US1, FR-070)."""

import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.analytics_event import AnalyticsEvent

logger = logging.getLogger(__name__)


class AnalyticsEventCreate(BaseModel):
    """Request body for creating an analytics event."""

    event_type: str = Field(min_length=1, max_length=100)
    service: str = Field(min_length=1, max_length=100)
    endpoint: Optional[str] = Field(default=None, max_length=255)
    user_id: Optional[str] = Field(default=None, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalyticsEventRead(BaseModel):
    """Representation of a stored analytics event."""

    model_config = ConfigDict(from_attributes=True)

    event_id: str
    event_type: str
    service: str
    endpoint: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_json"
    )


def list_analytics_events(
    db: Session = Depends(get_db),
    service: Optional[str] = Query(default=None, max_length=100),
    event_type: Optional[str] = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AnalyticsEvent]:
    """List analytics events, optionally filtered by service or event type."""
    statement = select(AnalyticsEvent)
    if service is not None:
        statement = statement.where(AnalyticsEvent.service == service)
    if event_type is not None:
        statement = statement.where(AnalyticsEvent.event_type == event_type)

    statement = statement.order_by(AnalyticsEvent.timestamp.desc()).limit(limit)
    events = list(db.execute(statement).scalars().all())
    logger.info(
        "Listed analytics events",
        extra={"count": len(events), "service": service, "event_type": event_type},
    )
    return events


def get_analytics_event(event_id: str, db: Session = Depends(get_db)) -> AnalyticsEvent:
    """Get a single analytics event by its identifier."""
    event = db.get(AnalyticsEvent, event_id)
    if event is None:
        logger.warning("Analytics event not found", extra={"event_id": event_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics event '{event_id}' was not found",
        )
    logger.info("Fetched analytics event", extra={"event_id": event_id})
    return event


def create_analytics_event(
    payload: AnalyticsEventCreate,
    db: Session = Depends(get_db),
) -> AnalyticsEvent:
    """Create an analytics event."""
    event = AnalyticsEvent(
        event_type=payload.event_type,
        service=payload.service,
        endpoint=payload.endpoint,
        user_id=payload.user_id,
        metadata_json=payload.metadata,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info(
        "Created analytics event",
        extra={"event_id": event.event_id, "event_type": event.event_type},
    )
    return event
