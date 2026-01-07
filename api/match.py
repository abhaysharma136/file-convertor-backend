from fastapi import APIRouter
from fastapi import  UploadFile, File, BackgroundTasks, Form
from jobs.store import jobs,create_job
from datetime import datetime
from core.config import UPLOAD_DIR
import os
from jobs.workers import run_resume_jd_match
router = APIRouter(prefix="/jd/match", tags=["Match"])
@router.post("")
async def match_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    job_id = create_job("resume_jd_match")
    jobs[job_id]["jd_text"] = job_description

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = os.path.join(
        UPLOAD_DIR, f"{job_id}_{timestamp}_{file.filename}"
    )

    with open(input_path, "wb") as f:
        f.write(await file.read())

    jobs[job_id]["input_path"] = input_path

    background_tasks.add_task(run_resume_jd_match, job_id)

    return {
        "job_id": job_id,
        "status": "pending"
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
