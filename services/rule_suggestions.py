def generate_rule_based_suggestions(extracted_text, ats_result):
    suggestions = []
    rewritten_bullets = []
    missing_keywords = []

    sections = extracted_text.get("sections", {})
    breakdown = ats_result.get("breakdown", {})
    score = ats_result.get("ats_score", 0)

    # ----------------------------
    # Determine Severity Context
    # ----------------------------
    if score < 50:
        base_severity = "critical"
    elif score < 70:
        base_severity = "moderate"
    else:
        base_severity = "minor"

    # ----------------------------
    # 1️⃣ STRUCTURE (Max 20)
    # ----------------------------
    structure_score = breakdown.get("structure", 0)

    if structure_score < 15:
        if not sections.get("skills"):
            suggestions.append({
                "title": "Missing Skills Section",
                "description": (
                    "Add a dedicated Skills section to improve ATS parsing and keyword recognition."
                ),
                "severity": "critical",
                "category": "structure"
            })

        if not sections.get("experience"):
            suggestions.append({
                "title": "Missing Experience Section",
                "description": (
                    "Include a clearly labeled Experience section to help recruiters quickly evaluate your background."
                ),
                "severity": "critical",
                "category": "structure"
            })

        if not sections.get("education"):
            suggestions.append({
                "title": "Missing Education Section",
                "description": (
                    "Add an Education section to ensure completeness and ATS compatibility."
                ),
                "severity": "moderate",
                "category": "structure"
            })

    # ----------------------------
    # 2️⃣ EXPERIENCE DEPTH (Max 20)
    # ----------------------------
    experience_score = breakdown.get("experience_depth", 0)

    if experience_score < 12:
        suggestions.append({
            "title": "Experience Section Needs More Depth",
            "description": (
                "Expand your experience descriptions. Add more details about responsibilities, tools used, and outcomes."
            ),
            "severity": base_severity,
            "category": "experience"
        })

        exp_text = sections.get("experience", "")
        if exp_text:
            rewritten_bullets.append(
                "Led cross-functional initiatives to deliver measurable business impact and improve operational efficiency."
            )

    # ----------------------------
    # 3️⃣ IMPACT & METRICS (Max 15)
    # ----------------------------
    impact_score = breakdown.get("impact", 0)

    if impact_score < 10:
        suggestions.append({
            "title": "Add Measurable Impact",
            "description": (
                "Include quantifiable achievements (%, revenue, users, performance improvements, cost reduction). "
                "Metrics significantly improve ATS and recruiter perception."
            ),
            "severity": base_severity,
            "category": "impact"
        })

    # ----------------------------
    # 4️⃣ SKILL DIVERSITY (Max 15)
    # ----------------------------
    skill_score = breakdown.get("skill_diversity", 0)

    if skill_score < 10:
        suggestions.append({
            "title": "Expand Skills Diversity",
            "description": (
                "Broaden and structure your skills section to reflect tools, methodologies, and domain expertise clearly."
            ),
            "severity": "moderate",
            "category": "skills"
        })

    # ----------------------------
    # 5️⃣ CLARITY & ACTION VERBS (Max 15)
    # ----------------------------
    clarity_score = breakdown.get("clarity", 0)

    if clarity_score < 10:
        suggestions.append({
            "title": "Use Stronger Action Verbs",
            "description": (
                "Replace weak phrases like 'responsible for' with strong action verbs such as "
                "'led', 'developed', 'optimized', or 'implemented'."
            ),
            "severity": "moderate",
            "category": "clarity"
        })

    # ----------------------------
    # 6️⃣ LENGTH (Max 15)
    # ----------------------------
    length_score = breakdown.get("length", 0)

    if length_score < 10:
        suggestions.append({
            "title": "Resume Length Optimization",
            "description": (
                "Adjust resume length to maintain 1–2 pages. Ensure concise yet complete representation of experience."
            ),
            "severity": "minor",
            "category": "length"
        })

    # ----------------------------
    # OPTIONAL: Generic Missing Keywords Suggestion
    # ----------------------------
    normalized_text = extracted_text.get("normalized_text", "").lower()

    GENERIC_BUSINESS_TERMS = [
        "leadership", "collaboration", "strategy",
        "analysis", "optimization", "performance",
        "cross-functional"
    ]
    if score < 70:
        for term in GENERIC_BUSINESS_TERMS:
            if term not in normalized_text:
                missing_keywords.append(term)

    # ----------------------------
    # Final Structured Return
    # ----------------------------
    return {
        "suggestions": suggestions[:6],
        "rewritten_bullets": rewritten_bullets[:2],
        "missing_keywords": missing_keywords[:6]
    }
