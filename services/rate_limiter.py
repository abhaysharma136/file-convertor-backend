from datetime import datetime
from fastapi import Request, HTTPException
from utils.security import hash_ip
from core.logger import log_event
# In-memory store
rate_limit_store = {}

# Limits per service
LIMITS = {
    "resume": 3,
    "match": 3,
    "convert": 5,
}

def get_client_ip(request: Request) -> str:
    # Works behind proxies too
    if request.headers.get("x-forwarded-for"):
        return request.headers["x-forwarded-for"].split(",")[0]
    return request.client.host


def check_rate_limit(request: Request, service: str):
    ip = get_client_ip(request)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    key = f"{ip}:{service}:{today}"

    current = rate_limit_store.get(key, 0)
    limit = LIMITS[service]
    log_event({
        "event": "quota_check",
        "service": service,
        "ip_hash": hash_ip(ip),
        "used": current,
        "limit": limit
    })

    if current >= limit:
        log_event({
            "event": "quota_exceeded",
            "service": service,
            "ip_hash": hash_ip(ip),
            "limit": limit
        })

        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached for {service}. Try again tomorrow or upgrade.",
        )

    # Increment
    rate_limit_store[key] = current + 1

    log_event({
        "event": "quota_increment",
        "service": service,
        "ip_hash": hash_ip(ip),
        "new_used": current + 1,
        "limit": limit
    })
