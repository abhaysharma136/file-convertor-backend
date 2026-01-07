IMPORTANT_JD_KEYWORDS = [
    "python", "django", "react", "node", "aws",
    "api", "microservices", "docker", "ci/cd",
    "system design", "scalability"
]

def extract_jd_keywords(jd_text):
    return [k for k in IMPORTANT_JD_KEYWORDS if k in jd_text]

def calculate_jd_match(resume_text, jd_keywords):
    resume_text = resume_text.lower()

    matched = [k for k in jd_keywords if k in resume_text]
    missing = [k for k in jd_keywords if k not in resume_text]

    if not jd_keywords:
        return 0, [], []

    score = int((len(matched) / len(jd_keywords)) * 100)
    return score, matched, missing
