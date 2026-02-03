import time
import os
import threading
from jobs.store import jobs
from core.config import JOB_TTL_SECONDS
def cleanup_expired_jobs():
    now = time.time()
    expired_jobs = []

    for job_id, job in jobs.items():
        if now - job["created_at"] > JOB_TTL_SECONDS:
            expired_jobs.append(job_id)

    for job_id in expired_jobs:
        job = jobs[job_id]

        # Delete input file
        if job.get("input_path") and os.path.exists(job["input_path"]):
            os.remove(job["input_path"])

        # Delete output file
        if job.get("output_path") and os.path.exists(job["output_path"]):
            os.remove(job["output_path"])

        # Remove job metadata
        del jobs[job_id]


def start_cleanup_worker():
    def run():
        while True:
            print("🧹 cleanup tick")
            cleanup_expired_jobs()
            time.sleep(300)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()