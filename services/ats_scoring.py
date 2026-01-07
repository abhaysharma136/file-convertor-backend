def word_count(text: str) -> int:
    return len(text.split())


def score_sections(sections: dict):
    score = 0
    reasons = []

    required_sections = ["skills", "experience", "education", "projects"]

    for section in required_sections:
        if section in sections and sections[section]:
            score += 7
        else:
            reasons.append(f"Missing or weak '{section}' section")

    score = min(score, 30)
    return score, reasons

COMMON_TECH_SKILLS = [
    "python", "javascript", "react", "node", "django", "aws",
    "typescript", "sql", "mongodb", "api", "docker"
]

def score_skills(sections: dict):
    skills_text = sections.get("skills", "")
    score = 0
    reasons = []

    matched = [s for s in COMMON_TECH_SKILLS if s in skills_text]

    if len(matched) >= 8:
        score = 25
    elif len(matched) >= 5:
        score = 18
    elif len(matched) >= 3:
        score = 10
    else:
        reasons.append("Low technical skill coverage")
        score = 5

    return score, reasons

def score_experience(sections: dict):
    experience_text = sections.get("experience", "")
    wc = word_count(experience_text)
    reasons = []

    if wc > 250:
        return 25, []
    elif wc > 150:
        return 18, []
    elif wc > 80:
        return 10, []
    else:
        reasons.append("Experience section is too short or vague")
        return 5, reasons

def score_length(normalized_text: str):
    wc = word_count(normalized_text)
    reasons = []

    if 450 <= wc <= 800:
        return 20, []
    elif 350 <= wc < 450 or 800 < wc <= 950:
        return 15, []
    elif wc < 350:
        reasons.append("Resume is too short")
        return 8, reasons
    else:
        reasons.append("Resume is too long")
        return 8, reasons


def calculate_ats_score(extracted_text: dict):
    sections = extracted_text["sections"]
    normalized_text = extracted_text["normalized_text"]

    total_score = 0
    issues = []

    s1, r1 = score_sections(sections)
    s2, r2 = score_skills(sections)
    s3, r3 = score_experience(sections)
    s4, r4 = score_length(normalized_text)

    total_score = s1 + s2 + s3 + s4
    issues.extend(r1 + r2 + r3 + r4)

    return {
        "ats_score": total_score,
        "issues": issues,
        "breakdown": {
            "sections": s1,
            "skills": s2,
            "experience": s3,
            "length": s4
        }
    }
