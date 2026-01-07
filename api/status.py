from fastapi import APIRouter
from jobs.store import jobs
router = APIRouter(prefix="/status", tags=["Status"])

@router.get("/{job_id}")
def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"error": "Invalid job_id"}

    response = {
        "job_id": job_id,
        "status": job["status"]
    }

    if job["status"] == "completed":
        response["download_url"] = f"/convert/download/{job_id}"

    if job["status"] == "failed":
        response["error"] = job["error"]

    return response