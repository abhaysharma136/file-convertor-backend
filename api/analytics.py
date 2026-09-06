from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.dependencies import get_db
from models.analytics_event import AnalyticsEvent

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


class AnalyticsPayload(BaseModel):
    event_name: str
    feature: str | None = None
    source: str | None = None


@router.post("/track")
def track_event(
    payload: AnalyticsPayload,
    db: Session = Depends(get_db)
):
    event = AnalyticsEvent(
        event_name=payload.event_name,
        feature=payload.feature,
        source=payload.source
    )

    db.add(event)

    db.commit()

    return {
        "success": True
    }