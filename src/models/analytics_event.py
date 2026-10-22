"""AnalyticsEvent model - base entity shared across all user stories (data-model.md)"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class AnalyticsEvent(Base):
    """AnalyticsEvent - analytics capture entity."""

    __tablename__ = "analytics_events"

    event_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata", JSON, nullable=True, default=dict
    )

    __table_args__ = (
        Index("ix_analytics_events_service", "service"),
        Index("ix_analytics_events_timestamp", "timestamp"),
    )
