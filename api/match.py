from fastapi import APIRouter
from fastapi import  UploadFile, File, BackgroundTasks, Form, Request, HTTPException
from jobs.store import jobs,create_job
from datetime import datetime
from core.config import UPLOAD_DIR
import os
from jobs.workers import run_resume_jd_match
from services.rate_limiter import check_rate_limit
from services.credits import authorize_usage,get_credits,CREDIT_COST,get_remaining_free,consume_credit
from utils.security import hash_ip
from core.logger import log_event

router = APIRouter(prefix="/jd/match", tags=["Match"])
@router.post("")
async def match_resume(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    ip_hash = hash_ip(request.client.host)

    # 🔒 PREMIUM GATE: Credit Required
    if not consume_credit(ip_hash, "jd_match"):
        raise HTTPException(
            status_code=402,
            detail="JD Match requires 1 credit. Please purchase credits."
        )

    # ✅ Credit successfully reserved
    job_id = create_job("resume_jd_match")

    jobs[job_id]["jd_text"] = job_description
    jobs[job_id]["usage_mode"] = "credit"
    jobs[job_id]["ip_hash"] = ip_hash

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = os.path.join(
        UPLOAD_DIR,
        f"{job_id}_{timestamp}_{file.filename}"
    )

    with open(input_path, "wb") as f:
        f.write(await file.read())

    jobs[job_id]["input_path"] = input_path

    background_tasks.add_task(run_resume_jd_match, job_id)

    log_event({
        "event": "job_created",
        "job_id": job_id,
        "job_type": "resume_jd_match",
        "usage_mode": "credit"
    })

    return {
        "job_id": job_id,
        "status": "pending",
        "credits_remaining": get_credits(ip_hash)
    }


@router.get("/result/{job_id}")
def get_match_result(job_id: str):
    job = jobs.get(job_id)

    if not job or job["job_type"] != "resume_jd_match":
        return {"error": "Invalid job_id"}

    if job["status"] != "completed":
        return {"status": job["status"]}

    return {
        "status": "completed",
        "result": job["match_result"]
    }
