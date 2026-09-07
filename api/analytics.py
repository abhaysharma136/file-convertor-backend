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
    session_id: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None


@router.post("/track")
def track_event(
    payload: AnalyticsPayload,
    db: Session = Depends(get_db)
):
    event = AnalyticsEvent(
        event_name=payload.event_name,
        feature=payload.feature,
        source=payload.source,
        session_id=payload.session_id,
        utm_source=payload.utm_source,
        utm_medium=payload.utm_medium,
        utm_campaign=payload.utm_campaign,
    )

    db.add(event)

    db.commit()

    return {
        "success": True
    }