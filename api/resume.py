from fastapi import APIRouter
from fastapi import  UploadFile, File, BackgroundTasks
from core.config import UPLOAD_DIR
from jobs.workers import run_resume_analysis
from jobs.store import create_job, jobs
import os
from datetime import datetime

router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/analyze")
async def analyze_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    job_id = create_job("resume_analysis")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = os.path.join(
        UPLOAD_DIR, f"{job_id}_{timestamp}_{file.filename}"
    )

    with open(input_path, "wb") as f:
        f.write(await file.read())

    jobs[job_id]["input_path"] = input_path

    background_tasks.add_task(run_resume_analysis, job_id)

    return {
        "job_id": job_id,
        "status": "pending"
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