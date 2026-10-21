"""AnalyticsEvent model - base entity shared across all user stories (data-model.md)"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, func

Base = object()  # Placeholder - full SQLAlchemy model defined in data-model.md


class AnalyticsEvent:
    """AnalyticsEvent - simplified model for API implementation"""
    __tablename__ = "analytics_events"
    
    def __init__(self, event_type: str, service: str, endpoint: str = None, metadata: dict = None):
        self.event_type = event_type
        self.service = service
        self.endpoint = endpoint
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)
