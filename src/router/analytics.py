"""Analytics router - API endpoints for advanced analytics (US1, FR-070)."""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.analytics_event import AnalyticsEvent

router = APIRouter(prefix="/analytics", tags=["analytics"])


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


@router.get("/events", response_model=list[AnalyticsEventRead])
def list_analytics_events(
    db: Session = Depends(get_db),
    service: Optional[str] = Query(default=None, max_length=100),
    event_type: Optional[str] = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=200),
):
    """List analytics events, optionally filtered by service or event type."""
    statement = select(AnalyticsEvent)
    if service is not None:
        statement = statement.where(AnalyticsEvent.service == service)
    if event_type is not None:
        statement = statement.where(AnalyticsEvent.event_type == event_type)

    statement = statement.order_by(AnalyticsEvent.timestamp.desc()).limit(limit)
    return list(db.execute(statement).scalars().all())


@router.get("/events/{event_id}", response_model=AnalyticsEventRead)
def get_analytics_event(event_id: str, db: Session = Depends(get_db)):
    """Get a single analytics event by its identifier."""
    event = db.get(AnalyticsEvent, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics event '{event_id}' was not found",
        )
    return event


@router.post(
    "/events",
    response_model=AnalyticsEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_analytics_event(
    payload: AnalyticsEventCreate,
    db: Session = Depends(get_db),
):
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
    return event
