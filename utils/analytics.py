from sqlalchemy.orm import Session

from models.analytics_event import AnalyticsEvent


def track_event(
    db: Session,
    event_name: str,
    feature: str | None = None,
    source: str | None = None,
):
    event = AnalyticsEvent(
        event_name=event_name,
        feature=feature,
        source=source
    )

    db.add(event)

    db.commit()