from fastapi import APIRouter
from fastapi import  UploadFile, File, BackgroundTasks, Request, HTTPException, Form
from core.config import UPLOAD_DIR
from jobs.workers import run_resume_analysis
from jobs.store import create_job, jobs
import os
from datetime import datetime
from services.rate_limiter import check_rate_limit
from services.credits import authorize_usage,get_credits,get_remaining_free,CREDIT_COST
from utils.security import hash_ip
router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/analyze")
async def analyze_resume(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    useCredit: bool = Form(False),
):
    ip_hash = hash_ip(request.client.host)

    # ---------- Authorization ----------
    if useCredit:
        # User explicitly wants AI
        if get_credits(ip_hash) < CREDIT_COST["resume_analyzer"]:
            raise HTTPException(
                status_code=402,
                detail="Not enough credits. Please upgrade."
            )

        auth = {
            "allowed": True,
            "mode": "credit",
            "remaining_free": get_remaining_free(ip_hash, "resume_analyzer")
        }
    else:
        # User wants free quota
        auth = authorize_usage(
            ip_hash,
            "resume_analyzer",
            use_credit=useCredit,
            allow_credit_fallback=False
        )


        if not auth["allowed"]:
            raise HTTPException(
                status_code=429,
                detail="Daily free limit reached."
            )

    # ---------- Create job ----------
    job_id = create_job("resume_analysis")

    jobs[job_id]["usage_mode"] = auth["mode"]      # free | credit
    jobs[job_id]["remaining_free"] = auth["remaining_free"]
    jobs[job_id]["ip_hash"] = ip_hash

    # ---------- Save file ----------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = os.path.join(
        UPLOAD_DIR, f"{job_id}_{timestamp}_{file.filename}"
    )

    with open(input_path, "wb") as f:
        f.write(await file.read())

    jobs[job_id]["input_path"] = input_path

    # ---------- Background processing ----------
    background_tasks.add_task(run_resume_analysis, job_id)

    return {
        "job_id": job_id,
        "status": "pending",
        "usage": auth
    }

@router.get("/result/{job_id}")
def get_resume_result(job_id: str):
    job = jobs.get(job_id)

    if not job or job["job_type"] != "resume_analysis":
        return {"error": "Invalid job_id"}

    if job["status"] != "completed":
        return {"status": job["status"]}

    return {
        "status": "completed",
        "result": job["result"]
    }