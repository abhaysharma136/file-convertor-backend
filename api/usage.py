from fastapi import APIRouter, Request, HTTPException
from services.credits import get_remaining_free,get_credits,FREE_DAILY_LIMITS
from utils.security import hash_ip
router = APIRouter(prefix="/usage", tags=["Usage"])


VALID_SERVICES = {
    "resume": "resume_analyzer",
    "jd_match": "jd_match",
    "convert": "converter"
}

@router.get("/{service}")
def get_usage(service: str, request: Request):
    try:
        if service not in VALID_SERVICES:
            raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_service",
                        "message": f"Service '{service}' is not valid. Valid services are: {list(VALID_SERVICES.keys())}",
                        "available_services": list(VALID_SERVICES.keys())
                    }
                )

        internal_service = VALID_SERVICES[service]

        ip_hash = hash_ip(request.client.host)

        remaining_free = get_remaining_free(ip_hash, internal_service)
        credits_left = get_credits(ip_hash)

        daily_limit = FREE_DAILY_LIMITS[internal_service]

        can_run = remaining_free > 0 or credits_left > 0

        return {
            "service": service,
            "remaining_free": max(0, remaining_free),
            "daily_limit": daily_limit,
            "credits_left": credits_left,
            "can_run": can_run
        }
    except HTTPException:
        # 🔑 Let FastAPI handle expected errors
        raise

    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An unexpected error occurred"
            }
        )