
from fastapi import APIRouter
from jobs.store import jobs, create_job
import os
from fastapi import  UploadFile, File, BackgroundTasks, Form, Request, HTTPException
from datetime import datetime
from core.config import UPLOAD_DIR, OUTPUT_DIR
from jobs.workers import run_conversion
from fastapi.responses import FileResponse
from services.rate_limiter import check_rate_limit
from services.credits import authorize_usage
from utils.security import hash_ip
router = APIRouter(prefix="/convert", tags=["Conversion"])

@router.post("")
async def convert_file(request:Request,background_tasks:BackgroundTasks, file: UploadFile = File(...),target_format: str = Form(...)):
    ip_hash = hash_ip(request.client.host)

    auth = authorize_usage(ip_hash, "converter")

    if not auth["allowed"]:
        raise HTTPException(
            status_code=429,
            detail="Daily limit reached. Upgrade to continue."
        )
    
    # Read the file content
    contents = await file.read()
    job_id = create_job("conversion")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    with open(input_path, "wb") as f:
            f.write(contents)
    jobs[job_id]["input_path"] = input_path
    jobs[job_id]["status"] = "pending"

    # Decide conversion
    SUPPORTED_CONVERSIONS = {
        "image/png": ["jpg"],
        "application/pdf": ["docx"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ["pdf"],
    }

    allowed = SUPPORTED_CONVERSIONS.get(file.content_type)
    if not allowed or target_format not in allowed:
        jobs[job_id]["status"] = "failed"
        return {"error": "Unsupported conversion"}
    
    output_filename = f"{job_id}.{target_format}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    background_tasks.add_task(
        run_conversion,
        job_id,
        input_path,
        output_path,
        target_format
    )

    return {
        "job_id": job_id,
        "status": "pending",
        "usage":auth
    }




@router.get("/download/{job_id}")
def download(job_id: str):
    job = jobs.get(job_id)

    if not job or job["status"] != "completed":
        return {"error": "File not ready"}

    return FileResponse(
        job["output_path"],
        filename=os.path.basename(job["output_path"])
    )

