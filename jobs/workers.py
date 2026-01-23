from jobs.store import jobs
from services.ats_scoring import calculate_ats_score
from services.resume_parser import extract_resume_text,split_into_sections,normalize_text, normalize_jd_text
from services.ai_suggestions import generate_ai_suggestions
from services.rule_suggestions import generate_rule_based_suggestions
from services.jd_matching import extract_jd_keywords, calculate_jd_match
from services.conversion import convert_document
from PIL import Image
import time
from core.logger import log_event
def run_resume_analysis(job_id: str):
    try:
        start_time = time.time()

        log_event({
            "event": "job_started",
            "job_id": job_id,
            "job_type": "resume_analysis",
            "service": "resume"
        })
        jobs[job_id]["status"] = "processing"

        input_path = jobs[job_id]["input_path"]

        # 1. Extract text
        raw_text = extract_resume_text(input_path)
        
        sections = split_into_sections(raw_text)
        normalized_text = normalize_text(raw_text)

        jobs[job_id]["extracted_text"] = {
            "raw_text": raw_text,
            "normalized_text": normalized_text,
            "sections": sections
        }

        # Placeholder result (Day-3 replaces this)
        ats_result = calculate_ats_score(jobs[job_id]["extracted_text"])

        jobs[job_id]["result"] = ats_result

        try:
            ai_suggestions = generate_ai_suggestions(
                jobs[job_id]["extracted_text"],
                jobs[job_id]["result"]
            )
        except Exception:
            ai_suggestions = generate_rule_based_suggestions(
                jobs[job_id]["extracted_text"],
                jobs[job_id]["result"]
            )
        jobs[job_id]["result"]["suggestion_source"] = (
            "ai" if "error" not in ai_suggestions else "rules"
        )

        jobs[job_id]["result"]["ai_suggestions"] = ai_suggestions

        log_event({
            "event": "job_completed",
            "job_id": job_id,
            "job_type": "resume_analysis",
            "duration_ms": int((time.time() - start_time) * 1000),
            "ats_score": jobs[job_id]["result"]["ats_score"],
            "suggestion_source": jobs[job_id]["result"]["suggestion_source"]
        })

        
        jobs[job_id]["status"] = "completed"

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
      
        log_event({
        "event": "job_failed",
        "job_id": job_id,
        "job_type": "resume_analysis",
        "error": str(e)
    })

def run_resume_jd_match(job_id: str):
    try:
        start_time = time.time()

        log_event({
            "event": "job_started",
            "job_id": job_id,
            "job_type": "resume_jd_match",
            "service":"match"
        })

        jobs[job_id]["status"] = "processing"

        # 1. Extract resume text FIRST
        raw_text = extract_resume_text(jobs[job_id]["input_path"])
        normalized_text = normalize_text(raw_text)

        jobs[job_id]["extracted_text"] = {
            "raw_text": raw_text,
            "normalized_text": normalized_text,
        }

        # 2. Normalize JD
        jd_text = normalize_jd_text(jobs[job_id]["jd_text"])

        # 3. Keyword matching
        jd_keywords = extract_jd_keywords(jd_text)

        score, matched, missing = calculate_jd_match(
            normalized_text,
            jd_keywords
        )

        jobs[job_id]["match_result"] = {
            "match_score": score,
            "matched_keywords": matched,
            "missing_keywords": missing,
        }
        
        log_event({
            "event": "job_completed",
            "job_id": job_id,
            "job_type": "resume_jd_match",
            "duration_ms": int((time.time() - start_time) * 1000),
            "match_score": jobs[job_id]["match_result"]["match_score"]
        })

        jobs[job_id]["status"] = "completed"

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

        log_event({
            "event": "job_failed",
            "job_id": job_id,
            "job_type": "resume_jd_match",
            "error": str(e)
        })






def run_conversion(job_id, input_path, output_path, target_format):
    try:
        start_time = time.time()

        log_event({
            "event": "job_started",
            "job_id": job_id,
            "job_type": "conversion",
            "service":"convert",
            "target_format": target_format
        })

        jobs[job_id]["status"] = "processing"

        if target_format == "jpg":
            image = Image.open(input_path)
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")
            image.save(output_path, "JPEG")

        elif target_format in ("pdf", "docx"):
            convert_document(input_path, output_path, target_format)

        jobs[job_id]["output_path"] = output_path
        log_event({
            "event": "job_completed",
            "job_id": job_id,
            "job_type": "conversion",
            "duration_ms": int((time.time() - start_time) * 1000),
            "target_format": target_format
        })

        jobs[job_id]["status"] = "completed"

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

        log_event({
            "event": "job_failed",
            "job_id": job_id,
            "job_type": "conversion",
            "error": str(e)
        })
