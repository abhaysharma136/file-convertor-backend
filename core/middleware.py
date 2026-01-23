import time
from fastapi import Request
from core.logger import log_event
from utils.security import hash_ip

async def logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = int((time.time() - start) * 1000)

    log_event({
        "event": "request_completed",
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "duration_ms": duration,
        "ip_hash": hash_ip(request.client.host),
        "service": request.url.path.split("/")[1]
    })

    return response
