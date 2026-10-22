"""FeatureFlag model - base entity for feature flag framework (FR-075, NFR-054)"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class FeatureFlag(Base):
    """FeatureFlag - feature flag framework entity"""

    __tablename__ = "feature_flags"

    flag_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    flag_name: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rollout_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    rollback_token: Mapped[str | None] = mapped_column(String(200), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata", JSON, nullable=True
    )
