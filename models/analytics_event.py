import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    event_name = Column(
        String,
        nullable=False,
        index=True
    )

    feature = Column(
        String,
        nullable=True
    )

    source = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )