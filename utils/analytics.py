from sqlalchemy.orm import Session

from models.analytics_event import AnalyticsEvent


def track_event(
    db: Session,
    event_name: str,
    feature: str | None = None,
    source: str | None = None,
    session_id: str | None = None,
    utm_source: str | None = None,
    utm_medium: str | None = None,
    utm_campaign: str | None = None,
):
    event = AnalyticsEvent(
        event_name=event_name,
        feature=feature,
        source=source,
        session_id=session_id,
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
    )

    db.add(event)

    db.commit()