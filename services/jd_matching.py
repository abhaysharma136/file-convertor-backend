import re

# --------------------------------------
# CONFIG
# --------------------------------------

STOPWORDS = {
    "and","or","with","the","a","to","of","in","for","on","as",
    "strong","experience","knowledge","ability","excellent",
    "responsibilities","requirements","candidate","role",
    "work","working","understanding"
}

MAX_JD_SKILLS = 15


# --------------------------------------
# 1️⃣ CLEAN TEXT
# --------------------------------------

def normalize_text_simple(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+\#\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# --------------------------------------
# 2️⃣ EXTRACT SIMPLE SKILLS FROM JD
# --------------------------------------

def extract_core_jd_skills(jd_text: str):
    jd_text = normalize_text_simple(jd_text)

    words = jd_text.split()
    skills = []

    for word in words:
        if len(word) < 3:
            continue
        if word in STOPWORDS:
            continue
        if word.isdigit():
            continue
        skills.append(word)

    # deduplicate but preserve order
    seen = set()
    clean_skills = []
    for w in skills:
        if w not in seen:
            seen.add(w)
            clean_skills.append(w)

    return clean_skills[:MAX_JD_SKILLS]


# --------------------------------------
# 3️⃣ FREE MATCH ENGINE
# --------------------------------------

def calculate_jd_match_free(resume_sections: dict, jd_text: str):

    # Combine resume sections
    resume_text = " ".join([
        resume_sections.get("skills", ""),
        resume_sections.get("experience", ""),
        resume_sections.get("summary", "")
    ])

    resume_text = normalize_text_simple(resume_text)

    jd_skills = extract_core_jd_skills(jd_text)

    if not jd_skills:
        return {
            "match_score": 0,
            "alignment_level": "Unknown",
            "matched_core_skills": [],
            "critical_missing_skills": [],
            "summary_insight": "Unable to extract job requirements."
        }

    matched = []
    missing = []

    for skill in jd_skills:
        if re.search(rf"\b{re.escape(skill)}\b", resume_text):
            matched.append(skill)
        else:
            missing.append(skill)

    score = int((len(matched) / len(jd_skills)) * 100)

    # --------------------------------------
    # Alignment Level
    # --------------------------------------

    if score >= 75:
        alignment = "Strong"
        insight = "Your resume is strongly aligned with this job."
    elif score >= 50:
        alignment = "Moderate"
        insight = "Your resume matches some core requirements but is missing important skills."
    else:
        alignment = "Poor"
        insight = "Your resume is weakly aligned with this role. Tailoring is recommended."

    return {
        "match_score": score,
        "alignment_level": alignment,
        "matched_core_skills": matched[:8],
        "critical_missing_skills": missing[:8],
        "summary_insight": insight
    }
