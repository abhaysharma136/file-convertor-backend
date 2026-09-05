from fastapi import (
    APIRouter,
    UploadFile,
    File,
    BackgroundTasks,
    Request,
    HTTPException,
)

from core.config import UPLOAD_DIR
from jobs.workers import run_resume_analysis
from jobs.store import create_job, jobs

import os
from datetime import datetime

from services.rate_limiter import check_rate_limit

from utils.analytics import track_event
from core.database import SessionLocal


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


# ---------------------------------------------------------
# Upload configuration
# ---------------------------------------------------------

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/analyze")
async def analyze_resume(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):

    # ---------------------------------------------------------
    # Validate filename / extension
    # ---------------------------------------------------------

    original_filename = file.filename or ""

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    # ---------------------------------------------------------
    # Validate MIME type
    # ---------------------------------------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF or DOCX file."
        )


    # ---------------------------------------------------------
    # Rate limiting
    # ---------------------------------------------------------

    check_rate_limit(request, "resume")
    # ---------------------------------------------------------
    # Create job
    # ---------------------------------------------------------

    job_id = create_job("resume_analysis")

    # ---------------------------------------------------------
    # Analytics
    # ---------------------------------------------------------

    db = SessionLocal()

    try:
        track_event(
            db=db,
            event_name="resume_analysis_started",
            feature="resume_analyzer",
            source="resume_page"
        )
    finally:
        db.close()

    jobs[job_id]["usage_mode"] = "free"

    # ---------------------------------------------------------
    # Generate safe server-side filename
    # ---------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    safe_filename = (
        f"{job_id}_{timestamp}{extension}"
    )

    input_path = os.path.join(
        UPLOAD_DIR,
        safe_filename
    )

    # ---------------------------------------------------------
    # Save file with size limit
    # ---------------------------------------------------------

    total_size = 0

    try:
        with open(input_path, "wb") as output_file:

            while True:
                chunk = await file.read(1024 * 1024)  # 1 MB

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    output_file.close()

                    if os.path.exists(input_path):
                        os.remove(input_path)

                    raise HTTPException(
                        status_code=400,
                        detail="File must be smaller than 5MB."
                    )

                output_file.write(chunk)

    except HTTPException:
        raise

    except Exception:
        if os.path.exists(input_path):
            os.remove(input_path)

        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file."
        )

    finally:
        await file.close()

    jobs[job_id]["input_path"] = input_path

    # ---------------------------------------------------------
    # Background processing
    # ---------------------------------------------------------

    background_tasks.add_task(
        run_resume_analysis,
        job_id
    )

    return {
        "job_id": job_id,
        "status": "pending"
    }


@router.get("/result/{job_id}")
def get_resume_result(job_id: str):

    job = jobs.get(job_id)

    if not job or job["job_type"] != "resume_analysis":
        raise HTTPException(
            status_code=404,
            detail="Invalid job_id"
        )

    if job["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail=job.get(
                "error",
                "Resume analysis failed"
            )
        )

    if job["status"] != "completed":
        return {
            "status": job["status"]
        }

    return {
        "status": "completed",
        "result": job["result"]
    }