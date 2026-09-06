from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from core.dependencies import get_db
from models.waitlist import WaitlistUser

router = APIRouter(
    prefix="/waitlist",
    tags=["Waitlist"]
)


class WaitlistRequest(BaseModel):
    email: EmailStr
    feature: str | None = None
    source: str | None = None


@router.post("/join")
def join_waitlist(
    payload: WaitlistRequest,
    db: Session = Depends(get_db)
):
    normalized_email = payload.email.strip().lower()
    existing_user = (
        db.query(WaitlistUser)
        .filter(WaitlistUser.email == normalized_email)
        .first()
    )

    if existing_user:
        return {
            "success": True,
            "message": "Already joined",
            "already_joined": True,
        }

    user = WaitlistUser(
        email=normalized_email,
        feature=payload.feature,
        source=payload.source
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "success": True,
        "message": "Joined successfully",
        "already_joined": False,
    }