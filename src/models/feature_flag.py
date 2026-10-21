"""FeatureFlag model - base entity for feature flag framework (FR-075, NFR-054)"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, func

from src.models import Base


class FeatureFlag(Base):
    """FeatureFlag - feature flag framework entity"""

    __tablename__ = "feature_flags"

    flag_id = Column(Integer, primary_key=True, autoincrement=False)
    flag_name = Column(String(200), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    rollout_percentage = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    rollback_token = Column(String(200), nullable=True)
    metadata = Column(JSON, nullable=True)
