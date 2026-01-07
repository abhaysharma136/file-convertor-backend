import uuid
from typing import Dict
import time 

jobs: Dict[str, dict] = {}
def create_job(job_type: str):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_type": job_type,   # 👈 NEW
        "status": "pending",      # pending | processing | completed | failed
        "input_path": None,
        "output_path": None,

        # Resume-specific fields
        "extracted_text": None,
        "result": None,

        "error": None,
        
        #Resume-jd-specific
        "jd_text": None,
        "match_result": None,

        "created_at": time.time()   # UNIX timestamp
    }
    return job_id