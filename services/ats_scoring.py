import re


# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

ACTION_VERBS = {
    "built",
    "developed",
    "designed",
    "led",
    "managed",
    "implemented",
    "optimized",
    "increased",
    "reduced",
    "created",
    "launched",
    "delivered",
    "executed",
    "improved",
    "automated",
    "architected",
    "engineered",
    "deployed",
    "migrated",
    "integrated",
    "configured",
    "refactored",
    "streamlined",
    "mentored",
    "coordinated",
    "analyzed",
    "resolved",
    "modernized",
    "scaled",
}


WEAK_PHRASES = [
    "responsible for",
    "worked on",
    "helped with",
    "involved in",
    "assisted in",
    "participated in",
    "was responsible for",
]


COMMON_SKILLS = {
    # Languages
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "go",
    "golang",
    "ruby",
    "php",
    "kotlin",
    "swift",
    "rust",

    # Frontend
    "react",
    "angular",
    "vue",
    "next.js",
    "nextjs",
    "html",
    "css",
    "tailwind",
    "redux",

    # Backend
    "node.js",
    "nodejs",
    "express",
    "express.js",
    "fastapi",
    "django",
    "flask",
    "spring",
    "spring boot",
    ".net",
    "asp.net",

    # Databases
    "postgresql",
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "sqlite",
    "oracle",
    "sql server",

    # Cloud / DevOps
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "jenkins",
    "github actions",
    "gitlab ci",
    "ci/cd",

    # Architecture / APIs
    "rest",
    "rest api",
    "graphql",
    "microservices",
    "api",
    "websocket",

    # Tools
    "git",
    "github",
    "gitlab",
    "jira",
    "postman",

    # Messaging
    "kafka",
    "rabbitmq",

    # Testing
    "pytest",
    "jest",
    "selenium",
    "cypress",

    # General
    "agile",
    "scrum",
    "linux",
}


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w+#.-]+\b", text))


def find_action_verbs(text: str) -> set:
    words = set(
        re.findall(
            r"\b[a-zA-Z][a-zA-Z-]+\b",
            text.lower()
        )
    )

    return words.intersection(ACTION_VERBS)


def count_weak_phrases(text: str) -> int:
    text = text.lower()

    return sum(
        text.count(phrase)
        for phrase in WEAK_PHRASES
    )


def find_quantified_evidence(text: str) -> list:
    """
    Detect quantified evidence that is likely to represent
    measurable resume impact.

    Metrics are considered stronger when they appear near
    action/result language rather than merely appearing anywhere
    in the resume.
    """

    metric_pattern = re.compile(
        r"""
        (?:
            \b\d+(?:\.\d+)?\s*%
            |
            \$\s?\d+(?:[,.]\d+)*(?:\s*[kmb])?
            |
            \b\d+(?:[,.]\d+)*\s*\+
            |
            \b\d+(?:\.\d+)?\s*x\b
            |
            \b\d+(?:[,.]\d+)*\s*(?:k|m|b)\b
            |
            \b\d+(?:[,.]\d+)*\s*
            (?:users?|customers?|clients?|requests?|transactions?|
            hours?|days?|months?|years?|engineers?|employees?|
            projects?|apis?|issues?|applications?|records?)
            |
            \b\d+(?:\.\d+)?\s*
            (?:ms|sec|seconds?|minutes?)
        )
        """,
        re.IGNORECASE | re.VERBOSE
    )

    matches = []

    # Split into reasonably independent resume statements.
    sentences = re.split(
        r"(?<=[.!?])\s+|(?<=\.)\s+(?=[a-z])",
        text
    )

    # Also handle PDF-extracted resumes where bullets may have
    # disappeared and statements simply run together.
    if len(sentences) == 1:
        sentences = re.split(
            r"\s+(?=(?:developed|built|designed|implemented|"
            r"improved|optimized|reduced|increased|created|"
            r"launched|delivered|automated|deployed|resolved|"
            r"managed|led|migrated|integrated|engineered)\b)",
            text,
            flags=re.IGNORECASE
        )

    action_words = {
        "developed",
        "built",
        "designed",
        "implemented",
        "improved",
        "optimized",
        "reduced",
        "increased",
        "created",
        "launched",
        "delivered",
        "automated",
        "deployed",
        "resolved",
        "managed",
        "led",
        "migrated",
        "integrated",
        "engineered",
        "scaled",
    }

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        metric_matches = metric_pattern.findall(sentence)

        if not metric_matches:
            continue

        words = set(
            re.findall(
                r"\b[a-zA-Z]+\b",
                sentence.lower()
            )
        )

        has_action = bool(
            words.intersection(action_words)
        )

        for match in metric_matches:

            # Metrics appearing in an achievement/action statement
            # are stronger evidence than standalone numbers.
            if has_action:
                matches.append(
                    f"impact:{match}"
                )
            else:
                matches.append(
                    f"metric:{match}"
                )

    return list(dict.fromkeys(matches))

def detect_skills(text: str) -> set:
    """
    Detect known technical/professional skills.

    This is deliberately a starter dictionary rather than
    attempting to maintain thousands of technologies.
    """

    normalized = text.lower()

    found = set()

    for skill in COMMON_SKILLS:

        # Escape special regex characters
        escaped = re.escape(skill)

        if re.search(
            rf"(?<!\w){escaped}(?!\w)",
            normalized
        ):
            found.add(skill)

    return found


def split_experience_bullets(experience_text: str) -> list:
    """
    Attempt to identify experience bullets even when PDF extraction
    removed the original bullet characters.

    First use explicit bullet markers.
    Otherwise treat sentence-like segments as content.
    """

    if not experience_text:
        return []

    # Explicit bullets
    bullet_parts = re.split(
        r"\s*[•●▪◦‣⁃]\s*|\s+[-*+]\s+",
        experience_text
    )

    bullet_parts = [
        part.strip()
        for part in bullet_parts
        if part.strip()
    ]

    if len(bullet_parts) > 1:
        return bullet_parts

    # Fallback: sentence-like chunks
    sentences = re.split(
        r"(?<=[.!?])\s+",
        experience_text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip().split()) >= 5
    ]


# ---------------------------------------------------------
# STRUCTURE — 20 POINTS
# ---------------------------------------------------------

def score_structure(sections: dict, metadata: dict):
    score = 0
    issues = []

    # Core sections
    core_sections = [
        "skills",
        "experience",
        "education",
    ]

    for section in core_sections:

        if sections.get(section):
            score += 5
        else:
            issues.append(
                f"Missing or weak '{section}' section"
            )

    # Contact information
    if metadata.get("email_present"):
        score += 1
    else:
        issues.append(
            "Email address was not detected"
        )

    if metadata.get("phone_present"):
        score += 1
    else:
        issues.append(
            "Phone number was not detected"
        )

    # Optional but useful
    if (
        metadata.get("linkedin_present")
        or metadata.get("github_present")
        or metadata.get("website_present")
    ):
        score += 2

    # Projects are useful, but not mandatory
    if sections.get("projects"):
        score += 1

    return min(score, 20), issues


# ---------------------------------------------------------
# LENGTH & CONTENT DENSITY — 15 POINTS
# ---------------------------------------------------------

def score_length(normalized_text: str):
    wc = count_words(normalized_text)
    issues = []

    if wc < 200:
        issues.append(
            "Resume appears very short and may not fully demonstrate your experience."
        )
        return 6, issues

    if wc < 300:
        return 10, issues

    if wc <= 1000:
        return 15, issues

    if wc <= 1300:
        issues.append(
            "Resume is becoming lengthy; consider removing repetitive content."
        )
        return 13, issues

    if wc <= 1600:
        issues.append(
            "Resume is quite long; consider tightening repetitive or low-value content."
        )
        return 11, issues

    issues.append(
        "Resume is very long; consider removing repetitive or less relevant content."
    )
    return 8, issues

# ---------------------------------------------------------
# EXPERIENCE QUALITY — 20 POINTS
# ---------------------------------------------------------

def score_experience_quality(sections: dict):
    text = sections.get("experience", "")

    if not text:
        return 0, [
            "Experience section is missing"
        ]

    issues = []

    bullets = split_experience_bullets(text)

    word_count = count_words(text)

    action_verbs = find_action_verbs(text)

    weak_hits = count_weak_phrases(text)

    quantified = find_quantified_evidence(text)

    score = 0

    # Content depth
    if word_count >= 300:
        score += 5
    elif word_count >= 180:
        score += 4
    elif word_count >= 100:
        score += 3
    else:
        score += 1
        issues.append(
            "Experience section needs more detail"
        )

    # Bullets
    if len(bullets) >= 6:
        score += 5
    elif len(bullets) >= 4:
        score += 4
    elif len(bullets) >= 2:
        score += 3
    else:
        score += 1
        issues.append(
            "Add more clearly separated achievement or responsibility bullets"
        )

    # Action language
    if len(action_verbs) >= 6:
        score += 5
    elif len(action_verbs) >= 4:
        score += 4
    elif len(action_verbs) >= 2:
        score += 3
    else:
        score += 1
        issues.append(
            "Use stronger action verbs in experience descriptions"
        )

    # Weak phrases
    if weak_hits == 0:
        score += 3
    elif weak_hits <= 2:
        score += 2
    else:
        score += 0
        issues.append(
            "Replace weak phrases such as 'responsible for' or 'worked on'"
        )

    # Metrics / outcomes
    if len(quantified) >= 4:
        score += 2
    elif len(quantified) >= 2:
        score += 1
    else:
        issues.append(
            "Add measurable results to more experience bullets"
        )

    return min(score, 20), issues


# ---------------------------------------------------------
# IMPACT & METRICS — 15 POINTS
# ---------------------------------------------------------

def score_quantified_impact(normalized_text: str):
    evidence = find_quantified_evidence(
        normalized_text
    )

    impact_evidence = [
        item
        for item in evidence
        if item.startswith("impact:")
    ]

    standalone_metrics = [
        item
        for item in evidence
        if item.startswith("metric:")
    ]

    issues = []

    impact_count = len(impact_evidence)
    total_count = len(evidence)

    if impact_count >= 5:
        return 15, issues

    if impact_count >= 3:
        return 13, issues

    if impact_count >= 2:
        return 11, issues

    if impact_count >= 1:
        return 9, [
            "Add measurable results to more experience or project bullets."
        ]

    if total_count >= 2:
        return 7, [
            "Move numerical details into achievement-focused bullets so their impact is clearer."
        ]

    return 5, [
        "Add measurable impact using percentages, numbers, scale, time, revenue, users, or performance metrics."
    ]

# ---------------------------------------------------------
# SKILLS — 15 POINTS
# ---------------------------------------------------------

def score_skills(sections: dict):
    text = sections.get("skills", "")

    if not text:
        return 0, [
            "Missing skills section"
        ]

    skills = detect_skills(text)

    issues = []

    count = len(skills)

    if count >= 15:
        return 15, issues

    if count >= 10:
        return 13, issues

    if count >= 7:
        return 11, issues

    if count >= 4:
        return 8, [
            "Expand the skills section with relevant tools, technologies, and methodologies"
        ]

    return 5, [
        "Skills section appears limited; add relevant technical and professional skills"
    ]


# ---------------------------------------------------------
# CLARITY — 15 POINTS
# ---------------------------------------------------------

def score_clarity(normalized_text: str):
    action_verbs = find_action_verbs(normalized_text)

    weak_hits = count_weak_phrases(normalized_text)

    issues = []

    score = 0

    # Strong action language
    if len(action_verbs) >= 10:
        score += 9
    elif len(action_verbs) >= 7:
        score += 8
    elif len(action_verbs) >= 4:
        score += 6
    elif len(action_verbs) >= 2:
        score += 4
    else:
        score += 2
        issues.append(
            "Use stronger action verbs to describe your work"
        )

    # Weak language
    if weak_hits == 0:
        score += 6
    elif weak_hits <= 2:
        score += 4
        issues.append(
            "Replace weak phrases such as 'responsible for' and 'worked on'"
        )
    else:
        score += 1
        issues.append(
            "Several weak phrases reduce the impact of your experience descriptions"
        )

    return min(score, 15), issues


# ---------------------------------------------------------
# STRENGTH CLASSIFICATION
# ---------------------------------------------------------

def determine_strength(score: int):

    if score >= 85:
        return "Strong"

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Needs Improvement"

    return "Weak"


# ---------------------------------------------------------
# OPTIMIZATION TIPS
# ---------------------------------------------------------

def generate_optimization_tips(score, breakdown):

    tips = []

    if score < 85:
        return tips

    if breakdown["structure"] < 20:
        tips.append(
            "Make sure your contact information and major resume sections are clearly identifiable."
        )

    if breakdown["experience_quality"] < 20:
        tips.append(
            "Strengthen experience bullets with clearer actions, technical context, and outcomes."
        )

    if breakdown["impact"] < 15:
        tips.append(
            "Add more quantified achievements such as percentages, scale, response times, users, or cost savings."
        )

    if breakdown["skills"] < 15:
        tips.append(
            "Expand your skills section with relevant technologies, tools, and methodologies."
        )

    if breakdown["clarity"] < 15:
        tips.append(
            "Replace generic responsibility statements with concise action-oriented bullets."
        )

    return tips


# ---------------------------------------------------------
# MAIN ATS CALCULATION
# ---------------------------------------------------------

def calculate_ats_score(extracted_text: dict):

    sections = extracted_text.get(
        "sections",
        {}
    )

    normalized_text = extracted_text.get(
        "normalized_text",
        ""
    )

    metadata = extracted_text.get(
        "metadata",
        {}
    )

    issues = []

    # 1. Structure
    s1, r1 = score_structure(
        sections,
        metadata
    )

    # 2. Length
    s2, r2 = score_length(
        normalized_text
    )

    # 3. Experience
    s3, r3 = score_experience_quality(
        sections
    )

    # 4. Impact
    s4, r4 = score_quantified_impact(
        normalized_text
    )

    # 5. Skills
    s5, r5 = score_skills(
        sections
    )

    # 6. Clarity
    s6, r6 = score_clarity(
        normalized_text
    )

    total_score = (
        s1 +
        s2 +
        s3 +
        s4 +
        s5 +
        s6
    )

    issues.extend(
        r1 +
        r2 +
        r3 +
        r4 +
        r5 +
        r6
    )

    breakdown = {
        "structure": s1,
        "length": s2,
        "experience_quality": s3,
        "impact": s4,
        "skills": s5,
        "clarity": s6,
    }

    optimization_tips = generate_optimization_tips(
        total_score,
        breakdown
    )

    return {
        "ats_score": total_score,
        "strength_level": determine_strength(
            total_score
        ),
        "issues": issues,
        "optimization_tips": optimization_tips,
        "breakdown": breakdown,
    }