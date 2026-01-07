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
        level = "critical"
    elif score < 70:
        level = "moderate"
    else:
        level = "minor"

    # ----------------------------
    # SECTION STRUCTURE
    # ----------------------------
    if breakdown["sections"] < 30:
        if not sections.get("skills"):
            suggestions.append(
                "Add a clear Technical Skills section to improve ATS readability."
            )
        if not sections.get("projects"):
            suggestions.append(
                "Include a Projects section to demonstrate hands-on experience."
            )

    # ----------------------------
    # EXPERIENCE QUALITY
    # ----------------------------
    if breakdown["experience"] < 20:
        if level in ("critical", "moderate"):
            suggestions.append(
                "Rewrite experience bullets using action verbs and measurable impact (e.g., scale, performance, users)."
            )
        else:
            suggestions.append(
                "Polish experience bullets by adding outcomes or metrics."
            )

        exp = sections.get("experience", "")
        if exp:
            rewritten_bullets.append(
                "Led end-to-end development of scalable features, improving system performance and reliability."
            )

    # ----------------------------
    # RESUME LENGTH
    # ----------------------------
    if breakdown["length"] < 15:
        suggestions.append(
            "Expand resume content slightly to better showcase achievements and responsibilities."
        )

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
    # RETURN TRIMMED OUTPUT
    # ----------------------------
    return {
        "suggestions": suggestions[:5],
        "rewritten_bullets": rewritten_bullets[:2],
        "missing_keywords": missing_keywords[:5],
        "severity": level
    }
