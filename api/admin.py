from fastapi import APIRouter, Request, HTTPException
from services.credits import credit_store
from utils.security import hash_ip

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/add-credits")
def add_credits(
    request: Request,
    amount: int = 10
):
    """
    DEV ONLY:
    Adds credits to the current IP for testing
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    ip_hash = hash_ip(request.client.host)

    current = credit_store.get(ip_hash, 0)
    credit_store[ip_hash] = current + amount

    return {
        "message": "Credits added",
        "credits_added": amount,
        "total_credits": credit_store[ip_hash]
    }
