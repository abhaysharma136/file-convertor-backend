def generate_rule_based_suggestions(
    extracted_text,
    ats_result
):
    suggestions = []
    rewritten_bullets = []
    missing_keywords = []

    sections = extracted_text.get(
        "sections",
        {}
    )

    breakdown = ats_result.get(
        "breakdown",
        {}
    )

    score = ats_result.get(
        "ats_score",
        0
    )

    # -----------------------------------------------------
    # Severity
    # -----------------------------------------------------

    if score < 50:
        base_severity = "critical"
    elif score < 70:
        base_severity = "moderate"
    else:
        base_severity = "minor"

    # -----------------------------------------------------
    # STRUCTURE
    # -----------------------------------------------------

    structure_score = breakdown.get(
        "structure",
        0
    )

    if structure_score < 15:

        if not sections.get("skills"):
            suggestions.append({
                "title": "Add a Skills Section",
                "description": (
                    "Add a dedicated Skills section containing "
                    "relevant technologies, tools, and methodologies."
                ),
                "severity": "critical",
                "category": "structure"
            })

        if not sections.get("experience"):
            suggestions.append({
                "title": "Add an Experience Section",
                "description": (
                    "Include a clearly labeled Experience section "
                    "to make your professional background easier to parse."
                ),
                "severity": "critical",
                "category": "structure"
            })

        if not sections.get("education"):
            suggestions.append({
                "title": "Add an Education Section",
                "description": (
                    "Include your educational background in a clearly "
                    "labeled section."
                ),
                "severity": "moderate",
                "category": "structure"
            })

    # -----------------------------------------------------
    # EXPERIENCE QUALITY
    # -----------------------------------------------------

    experience_score = breakdown.get(
        "experience_quality",
        0
    )

    if experience_score < 12:

        suggestions.append({
            "title": "Strengthen Experience Bullets",
            "description": (
                "Make experience bullets more specific by describing "
                "what you built or changed, the technologies involved, "
                "and the resulting outcome."
            ),
            "severity": base_severity,
            "category": "experience"
        })

        if sections.get("experience"):
            rewritten_bullets.append(
                "Developed and improved technical solutions to "
                "deliver measurable business and operational outcomes."
            )

    # -----------------------------------------------------
    # IMPACT
    # -----------------------------------------------------

    impact_score = breakdown.get(
        "impact",
        0
    )

    if impact_score < 10:

        suggestions.append({
            "title": "Add Measurable Impact",
            "description": (
                "Where possible, quantify your achievements using "
                "percentages, users, revenue, response times, scale, "
                "cost savings, or other measurable results."
            ),
            "severity": base_severity,
            "category": "impact"
        })

    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

    skill_score = breakdown.get("skills", 0)

    if skill_score < 10:
        suggestions.append({
            "title": "Strengthen Your Skills Section",
            "description": (
                "Add relevant technologies, tools, frameworks, databases, "
                "cloud platforms, and methodologies."
            ),
            "severity": "moderate",
            "category": "skills"
        })
        # -----------------------------------------------------
        # CLARITY
        # -----------------------------------------------------

        clarity_score = breakdown.get(
            "clarity",
            0
        )

        if clarity_score < 10:

            suggestions.append({
                "title": "Use Stronger Action Language",
                "description": (
                    "Replace phrases such as 'responsible for' or "
                    "'worked on' with specific action verbs such as "
                    "'developed', 'implemented', 'optimized', or 'designed'."
                ),
                "severity": "moderate",
                "category": "clarity"
            })

        # -----------------------------------------------------
        # LENGTH
        # -----------------------------------------------------

        length_score = breakdown.get(
            "length",
            0
        )

        if length_score < 10:

            suggestions.append({
                "title": "Review Resume Length",
                "description": (
                    "Your resume appears either too short to fully "
                    "demonstrate your experience or unnecessarily long. "
                    "Focus on concise, relevant content."
                ),
                "severity": "minor",
                "category": "length"
            })

        # -----------------------------------------------------
        # IMPORTANT:
        # Do NOT generate generic missing keywords here.
        #
        # Without a Job Description, Applyra cannot know which
        # keywords are actually missing for a particular role.
        # -----------------------------------------------------

        return {
            "suggestions": suggestions[:6],
            "rewritten_bullets": rewritten_bullets[:2],
            "missing_keywords": missing_keywords[:6]
        }