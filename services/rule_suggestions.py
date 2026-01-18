def generate_rule_based_suggestions(extracted_text, ats_result):
    suggestions = []
    rewritten_bullets = []
    missing_keywords = []

    sections = extracted_text["sections"]
    breakdown = ats_result["breakdown"]
    score = ats_result["ats_score"]

    # ----------------------------
    # SCORE-BASED CONTEXT
    # ----------------------------
    if score < 50:
        base_severity = "critical"
    elif score < 70:
        base_severity = "moderate"
    else:
        base_severity = "minor"

    # ----------------------------
    # SECTION STRUCTURE
    # ----------------------------
    if breakdown["sections"] < 30:
        if not sections.get("skills"):
            suggestions.append({
                "title": "Missing Technical Skills Section",
                "description": (
                    "Add a clear Technical Skills section listing relevant tools and technologies "
                    "to improve ATS parsing and keyword matching."
                ),
                "severity": "critical",
                "category": "sections"
            })

        if not sections.get("projects"):
            suggestions.append({
                "title": "Projects Section Not Found",
                "description": (
                    "Include a Projects section to showcase hands-on experience and real-world implementations."
                ),
                "severity": "moderate",
                "category": "sections"
            })

    # ----------------------------
    # EXPERIENCE QUALITY
    # ----------------------------
    if breakdown["experience"] < 20:
        suggestions.append({
            "title": "Weak Experience Bullet Points",
            "description": (
                "Rewrite experience bullets using strong action verbs and measurable impact "
                "(e.g., performance gains, scale, users, revenue)."
            ),
            "severity": base_severity,
            "category": "experience"
        })

        exp = sections.get("experience", "")
        if exp:
            rewritten_bullets.append(
                "Led end-to-end development of scalable features, improving system performance and reliability."
            )

    # ----------------------------
    # RESUME LENGTH
    # ----------------------------
    if breakdown["length"] < 15:
        suggestions.append({
            "title": "Resume Length Is Suboptimal",
            "description": (
                "Expand resume content slightly to better highlight responsibilities, achievements, and impact."
            ),
            "severity": "minor",
            "category": "length"
        })

    # ----------------------------
    # SKILL KEYWORDS
    # ----------------------------
    COMMON_TECH_SKILLS = [
        "docker", "kubernetes", "microservices",
        "rest api", "ci/cd", "cloud", "system design"
    ]

    skills_text = sections.get("skills", "").lower()

    for skill in COMMON_TECH_SKILLS:
        if skill not in skills_text:
            missing_keywords.append(skill)

    # ----------------------------
    # RETURN STRUCTURED OUTPUT
    # ----------------------------
    return {
        "suggestions": suggestions[:5],
        "rewritten_bullets": rewritten_bullets[:2],
        "missing_keywords": missing_keywords[:5]
    }
