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
from services.ai_utils import estimate_tokens
import json
from core.config import AI_ENABLED, MAX_AI_TOKENS_PER_JOB
from core.ai_budget import can_use_ai,register_ai_call
from services.credits import consume_credit
def run_resume_analysis(job_id: str):
    start_time = time.time()

    try:
        job = jobs[job_id]
        usage_mode = job.get("usage_mode", "free")  # free | credit
        ip_hash = job.get("ip_hash")

        log_event({
            "event": "job_started",
            "job_id": job_id,
            "job_type": "resume_analysis",
            "usage_mode": usage_mode
        })

        jobs[job_id]["status"] = "processing"

        # 1️⃣ Extract text
        raw_text = extract_resume_text(job["input_path"])
        sections = split_into_sections(raw_text)
        normalized_text = normalize_text(raw_text)

        extracted = {
            "raw_text": raw_text,
            "normalized_text": normalized_text,
            "sections": sections
        }

        jobs[job_id]["extracted_text"] = extracted

        # 2️⃣ ATS score (always deterministic)
        ats_result = calculate_ats_score(extracted)
        jobs[job_id]["result"] = ats_result

        # 3️⃣ Decide if AI can run
        estimated_tokens = (
            estimate_tokens(normalized_text)
            + estimate_tokens(json.dumps(ats_result))
        )

        can_attempt_ai = (
            usage_mode == "credit"
            and AI_ENABLED.get("resume_analyzer")
            and estimated_tokens <= MAX_AI_TOKENS_PER_JOB
            and can_use_ai()
        )

        log_event({
            "event": "ai_decision",
            "job_id": job_id,
            "can_attempt_ai": can_attempt_ai,
            "estimated_tokens": estimated_tokens
        })

        # 4️⃣ Generate suggestions
        if can_attempt_ai:
            try:
                ai_suggestions = generate_ai_suggestions(extracted, ats_result)

                # ✅ AI SUCCESS → NOW deduct credit
                if not consume_credit(ip_hash, "resume_analyzer"):
                    raise RuntimeError("Credit deduction failed after AI success")

                register_ai_call()
                suggestion_source = "ai"

                log_event({
                    "event": "ai_success",
                    "job_id": job_id,
                    "tokens": estimated_tokens
                })

            except Exception as ai_error:
                # ❌ AI failed → NO credit deduction
                ai_suggestions = generate_rule_based_suggestions(extracted, ats_result)
                suggestion_source = "rules"

                log_event({
                    "event": "ai_failed",
                    "job_id": job_id,
                    "error": str(ai_error)
                })
        else:
            ai_suggestions = generate_rule_based_suggestions(extracted, ats_result)
            suggestion_source = "rules"

        # 5️⃣ Attach results
        jobs[job_id]["result"]["ai_suggestions"] = ai_suggestions
        jobs[job_id]["result"]["suggestion_source"] = suggestion_source

        jobs[job_id]["status"] = "completed"

        log_event({
            "event": "job_completed",
            "job_id": job_id,
            "duration_ms": int((time.time() - start_time) * 1000),
            "ats_score": ats_result["ats_score"],
            "suggestion_source": suggestion_source
        })

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

        log_event({
            "event": "job_failed",
            "job_id": job_id,
            "error": str(e)
        })


def run_resume_jd_match(job_id: str):
    start_time = time.time()
    job = jobs[job_id]

    usage_mode = job.get("usage_mode", "free")  # free | credit
    ip_hash = job.get("ip_hash")

    log_event({
        "event": "job_started",
        "job_id": job_id,
        "job_type": "resume_jd_match",
        "usage_mode": usage_mode
    })

    try:
        jobs[job_id]["status"] = "processing"

        # 1️⃣ Extract resume text
        raw_text = extract_resume_text(job["input_path"])
        normalized_text = normalize_text(raw_text)

        extracted = {
            "raw_text": raw_text,
            "normalized_text": normalized_text,
        }

        jobs[job_id]["extracted_text"] = extracted

        # 2️⃣ Normalize JD
        jd_text = normalize_jd_text(job["jd_text"])

        # 3️⃣ Keyword extraction
        jd_keywords = extract_jd_keywords(jd_text)

        # 4️⃣ Deterministic match scoring (ALWAYS RUNS)
        score, matched, missing = calculate_jd_match(
            normalized_text,
            jd_keywords
        )

        match_result = {
            "match_score": score,
            "matched_keywords": matched,
            "missing_keywords": missing,
        }

        suggestion_source = "rules"

        # 5️⃣ AI eligibility check
        estimated_tokens = (
            estimate_tokens(normalized_text)
            + estimate_tokens(jd_text)
        )

        can_attempt_ai = (
            usage_mode == "credit"
            and AI_ENABLED.get("jd_match", False)
            and estimated_tokens <= MAX_AI_TOKENS_PER_JOB
            and can_use_ai()
        )

        log_event({
            "event": "ai_decision",
            "job_id": job_id,
            "service": "jd_match",
            "usage_mode": usage_mode,
            "estimated_tokens": estimated_tokens,
            "can_attempt_ai": can_attempt_ai
        })

        # 6️⃣ AI enhancement (optional)
        if can_attempt_ai:
            try:
                ai_suggestions = generate_ai_suggestions(
                    extracted,
                    jd_text
                )

                # ✅ AI succeeded → NOW deduct credit
                if not consume_credit(ip_hash, "jd_match"):
                    raise RuntimeError("Credit deduction failed")
                
                register_ai_call()

                match_result["ai_suggestions"] = ai_suggestions
                suggestion_source = "ai"

                log_event({
                    "event": "ai_call",
                    "job_id": job_id,
                    "service": "jd_match",
                    "model": "gpt-4o-mini",
                    "estimated_tokens": estimated_tokens
                })

            except Exception as ai_error:
                # ❌ AI failed → NO credit deduction
                log_event({
                    "event": "ai_failed",
                    "job_id": job_id,
                    "service": "jd_match",
                    "error": str(ai_error)
                })


        # 7️⃣ Save result
        match_result["suggestion_source"] = suggestion_source
        jobs[job_id]["match_result"] = match_result

        jobs[job_id]["status"] = "completed"

        log_event({
            "event": "job_completed",
            "job_id": job_id,
            "job_type": "resume_jd_match",
            "duration_ms": int((time.time() - start_time) * 1000),
            "match_score": score,
            "suggestion_source": suggestion_source
        })

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
