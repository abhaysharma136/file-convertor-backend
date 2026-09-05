from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.dependencies import get_db
from models.analytics_event import AnalyticsEvent
from models.waitlist import WaitlistUser
from services.credits import credit_store
from utils.security import hash_ip
import os
import secrets
router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def require_admin(request: Request):
    expected_token = os.getenv("ADMIN_ANALYTICS_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="Admin authentication is not configured."
        )

    provided_token = request.headers.get("X-Admin-Token")

    if not provided_token or not secrets.compare_digest(
        provided_token,
        expected_token
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    return True
@router.post("/add-credits")
def add_credits(
    request: Request,
    amount: int = 10,
    _: bool = Depends(require_admin),
):
    """
    DEV ONLY:
    Adds credits to the current IP for testing
    """

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid amount"
        )

    ip_hash = hash_ip(request.client.host)

    current = credit_store.get(ip_hash, 0)

    credit_store[ip_hash] = current + amount

    return {
        "message": "Credits added",
        "credits_added": amount,
        "total_credits": credit_store[ip_hash]
    }


@router.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    # =========================================================
    # TOTALS
    # =========================================================

    total_users = db.query(WaitlistUser).count()

    total_events = db.query(AnalyticsEvent).count()

    # =========================================================
    # WAITLIST BREAKDOWNS
    # =========================================================

    feature_breakdown = (
        db.query(
            WaitlistUser.feature,
            func.count(WaitlistUser.id)
        )
        .group_by(WaitlistUser.feature)
        .all()
    )

    source_breakdown = (
        db.query(
            WaitlistUser.source,
            func.count(WaitlistUser.id)
        )
        .group_by(WaitlistUser.source)
        .all()
    )

    # =========================================================
    # CORE ANALYTICS COUNTS
    # =========================================================

    modal_opens = (
        db.query(AnalyticsEvent)
        .filter(
            AnalyticsEvent.event_name == "modal_open"
        )
        .count()
    )

    waitlist_joins = (
        db.query(AnalyticsEvent)
        .filter(
            AnalyticsEvent.event_name == "waitlist_join"
        )
        .count()
    )
    waitlist_already_joined = (
    db.query(AnalyticsEvent)
    .filter(
        AnalyticsEvent.event_name == "waitlist_already_joined"
    )
    .count()
)

    resume_analysis_started = (
        db.query(AnalyticsEvent)
        .filter(
            AnalyticsEvent.event_name == "resume_analysis_started"
        )
        .count()
    )

    resume_analysis_completed = (
        db.query(AnalyticsEvent)
        .filter(
            AnalyticsEvent.event_name == "resume_analysis_completed"
        )
        .count()
    )

    ai_feature_clicked = (
        db.query(AnalyticsEvent)
        .filter(
            AnalyticsEvent.event_name == "ai_feature_clicked"
        )
        .count()
    )
    homepage_cta_clicked = (
        db.query(AnalyticsEvent)
        .filter(
            AnalyticsEvent.event_name == "homepage_cta_clicked"
        )
        .count()
    )

    # =========================================================
    # FEATURE-LEVEL EVENT BREAKDOWN
    # =========================================================

    event_breakdown = (
        db.query(
            AnalyticsEvent.event_name,
            AnalyticsEvent.feature,
            func.count(AnalyticsEvent.id)
        )
        .group_by(
            AnalyticsEvent.event_name,
            AnalyticsEvent.feature
        )
        .all()
    )

    # =========================================================
    # WAITLIST CONVERSION BY FEATURE
    # =========================================================

    modal_opens_by_feature = (
        db.query(
            AnalyticsEvent.feature,
            func.count(AnalyticsEvent.id)
        )
        .filter(
            AnalyticsEvent.event_name == "modal_open"
        )
        .group_by(AnalyticsEvent.feature)
        .all()
    )

    waitlist_joins_by_feature = (
        db.query(
            AnalyticsEvent.feature,
            func.count(AnalyticsEvent.id)
        )
        .filter(
            AnalyticsEvent.event_name == "waitlist_join"
        )
        .group_by(AnalyticsEvent.feature)
        .all()
    )

    # Convert joins to lookup dict
    joins_lookup = {
        row[0]: row[1]
        for row in waitlist_joins_by_feature
    }

    feature_conversion = []

    for row in modal_opens_by_feature:
        feature = row[0]
        opens = row[1]

        joins = joins_lookup.get(feature, 0)

        conversion_rate = 0

        if opens > 0:
            conversion_rate = round(
                (joins / opens) * 100,
                2
            )

        feature_conversion.append({
            "feature": feature,
            "modal_opens": opens,
            "waitlist_joins": joins,
            "conversion_rate": conversion_rate
        })

    # =========================================================
    # OVERALL CONVERSION
    # =========================================================

    overall_conversion_rate = 0

    if modal_opens > 0:
        overall_conversion_rate = round(
            (waitlist_joins / modal_opens) * 100,
            2
        )

    # =========================================================
    # LATEST SIGNUPS
    # =========================================================

    latest_signups = (
        db.query(WaitlistUser)
        .order_by(WaitlistUser.created_at.desc())
        .limit(10)
        .all()
    )
    

    # =========================================================
    # RESPONSE
    # =========================================================

    return {
        "totals": {
            "waitlist_users": total_users,
            "events": total_events
        },

        "feature_breakdown": [
            {
                "feature": row[0],
                "count": row[1]
            }
            for row in feature_breakdown
        ],

        "source_breakdown": [
            {
                "source": row[0],
                "count": row[1]
            }
            for row in source_breakdown
        ],

        "analytics": {
            "modal_opens": modal_opens,

            "waitlist_joins": waitlist_joins,

            "waitlist_already_joined": waitlist_already_joined,

            "resume_analysis_started": resume_analysis_started,

            "resume_analysis_completed": resume_analysis_completed,

            "ai_feature_clicked": ai_feature_clicked,

            "overall_conversion_rate": overall_conversion_rate,

            "homepage_cta_clicked": homepage_cta_clicked,
        },

        "event_breakdown": [
            {
                "event_name": row[0],
                "feature": row[1],
                "count": row[2]
            }
            for row in event_breakdown
        ],

        "feature_conversion": feature_conversion,

        "latest_signups": [
            {
                "email": user.email,
                "feature": user.feature,
                "source": user.source,
                "created_at": user.created_at
            }
            for user in latest_signups
        ]
    }