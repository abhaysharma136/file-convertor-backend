# ----------------------------
# CONSTANTS
# ----------------------------

ACTION_VERBS = [
    "developed", "designed", "led", "managed", "implemented",
    "optimized", "increased", "reduced", "built", "created",
    "launched", "delivered", "executed", "improved"
]

WEAK_PHRASES = [
    "responsible for",
    "worked on",
    "helped with",
    "involved in",
    "assisted in"
]

REQUIRED_SECTIONS = [
    "skills",
    "experience",
    "education"
]

MAX_RAW_SCORE = 100


# ----------------------------
# SCORING FUNCTIONS
# ----------------------------

def score_structure(sections: dict):
    score = 0
    issues = []

    for sec in REQUIRED_SECTIONS:
        if sections.get(sec):
            score += 6
        else:
            issues.append(f"Missing or weak '{sec}' section")

    if sections.get("projects"):
        score += 2

    return min(score, 20), issues


def score_length(normalized_text: str):
    wc = len(normalized_text.split())
    issues = []

    if 450 <= wc <= 800:
        return 15, []
    elif 350 <= wc < 450 or 800 < wc <= 950:
        return 10, []
    elif wc < 350:
        issues.append("Resume is too short")
        return 8, issues
    else:
        issues.append("Resume is too long")
        return 8, issues


def score_experience_depth(sections: dict):
    text = sections.get("experience", "")
    wc = len(text.split())
    issues = []

    if wc > 250:
        return 20, []
    elif wc > 150:
        return 18, []
    elif wc > 80:
        return 10, []
    else:
        issues.append("Experience section is too short or vague")
        return 5, issues


def score_quantified_impact(normalized_text: str):
    percent_count = normalized_text.count("%")
    digit_count = sum(c.isdigit() for c in normalized_text)

    if percent_count >= 4 or digit_count > 30:
        return 15, []
    elif percent_count >= 1:
        return 10, []
    else:
        return 6, ["Add measurable impact using %, numbers, metrics"]


def score_skill_diversity(sections: dict):
    text = sections.get("skills", "")
    issues = []

    if not text:
        return 5, ["Missing skills section"]

    keyword_count = text.count(",") + text.count("•")

    if keyword_count > 20:
        return 15, []
    elif keyword_count > 12:
        return 12, []
    elif keyword_count > 6:
        return 9, []
    else:
        return 6, ["Expand and structure your skills section better"]


def score_clarity(normalized_text: str):
    weak_hits = sum(normalized_text.count(p) for p in WEAK_PHRASES)
    strong_hits = sum(normalized_text.count(v) for v in ACTION_VERBS)

    if strong_hits >= 5 and weak_hits == 0:
        return 15, []
    elif strong_hits >= 3:
        return 12, []
    elif strong_hits >= 1:
        return 9, []
    else:
        return 6, ["Use stronger action verbs to describe impact"]


# ----------------------------
# STRENGTH CLASSIFICATION
# ----------------------------

def determine_strength(score: int):
    if score >= 85:
        return "Strong"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Needs Improvement"
    else:
        return "Weak"


# ----------------------------
# OPTIMIZATION MODE (NEW)
# ----------------------------

def generate_optimization_tips(score, breakdown):
    """
    Only runs when score is already strong (>=85).
    Adds section-specific refinements.
    """
    tips = []

    if score < 85:
        return tips  # Only optimize strong resumes

    if breakdown["length"] < 15:
        tips.append(
            "Fine-tune resume length to fall within the optimal 450–800 word range for recruiter scanning efficiency."
        )

    if breakdown["experience_depth"] < 20:
        tips.append(
            "Deepen experience bullets with more technical context, tools used, or business impact."
        )

    if breakdown["impact"] < 15:
        tips.append(
            "Add more quantified achievements (%, scale, performance gains, revenue impact) to strengthen executive appeal."
        )

    if breakdown["skill_diversity"] < 15:
        tips.append(
            "Broaden your skills section to include architecture, leadership, or domain-specific capabilities."
        )

    if breakdown["clarity"] < 15:
        tips.append(
            "Strengthen action verbs and eliminate weak phrasing to improve leadership presence."
        )

    return tips


# ----------------------------
# MAIN ATS CALCULATION
# ----------------------------

def calculate_ats_score(extracted_text: dict):

    sections = extracted_text.get("sections", {})
    normalized_text = extracted_text.get("normalized_text", "")

    issues = []

    s1, r1 = score_structure(sections)
    s2, r2 = score_length(normalized_text)
    s3, r3 = score_experience_depth(sections)
    s4, r4 = score_quantified_impact(normalized_text)
    s5, r5 = score_skill_diversity(sections)
    s6, r6 = score_clarity(normalized_text)

    total_score = s1 + s2 + s3 + s4 + s5 + s6

    issues.extend(r1 + r2 + r3 + r4 + r5 + r6)

    breakdown = {
        "structure": s1,
        "length": s2,
        "experience_depth": s3,
        "impact": s4,
        "skill_diversity": s5,
        "clarity": s6
    }

    optimization_tips = generate_optimization_tips(total_score, breakdown)

    return {
        "ats_score": total_score,
        "strength_level": determine_strength(total_score),
        "issues": issues,
        "optimization_tips": optimization_tips,
        "breakdown": breakdown
    }
