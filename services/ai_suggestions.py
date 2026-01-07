import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")
client = OpenAI(api_key=OPENAI_API_KEY)

def build_ai_prompt(extracted_text, ats_result):
    return f"""
You are an expert technical resume reviewer.

Resume sections:
Skills: {extracted_text['sections'].get('skills', '')}
Experience: {extracted_text['sections'].get('experience', '')}
Projects: {extracted_text['sections'].get('projects', '')}

ATS Score: {ats_result['ats_score']}
Score Breakdown: {ats_result['breakdown']}

Tasks:
1. Suggest 3–5 concrete improvements to increase ATS score.
2. Rewrite 2 experience bullets to be more impact-driven.
3. Suggest missing technical keywords (if any).
4. Keep suggestions concise and practical.

Output JSON ONLY in this format:
{{
  "suggestions": [],
  "rewritten_bullets": [],
  "missing_keywords": []
}}
"""

def generate_ai_suggestions(extracted_text, ats_result):
    prompt = build_ai_prompt(extracted_text, ats_result)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return json.loads(response.choices[0].message.content)