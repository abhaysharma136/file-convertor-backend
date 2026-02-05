import os
from dotenv import load_dotenv


load_dotenv()
ENV = os.getenv("ENV", "development")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print("Base_dir", BASE_DIR)
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
# print("Storage_dir", STORAGE_DIR)
UPLOAD_DIR = os.path.join(STORAGE_DIR, "uploads")
OUTPUT_DIR = os.path.join(STORAGE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

JOB_TTL_SECONDS = 30 * 60  # 30 minutes


# Credits pricing config

FREE_DAILY_LIMITS = {
    "resume_analyzer": 1,
    "jd_match": 1,
    "converter": 1
}

CREDIT_COST = {
    "resume_analyzer": 1,
    "jd_match": 1,
    "converter": 0
}

# AI Guardrails

# ---- AI Guardrails ----
APPLYRA_AI_GLOBAL_ENABLED = os.getenv(
    "APPLYRA_AI_GLOBAL_ENABLED", "true"
).lower() == "true"

MAX_AI_TOKENS_PER_JOB = int(
    os.getenv("MAX_AI_TOKENS_PER_JOB",2500)
)

MAX_AI_CALLS_PER_DAY = int(
    os.getenv("MAX_AI_CALLS_PER_DAY", "500")
)
print("ENV", ENV)
AI_ENABLED = {
    "resume_analyzer": os.getenv("AI_RESUME_ANALYZER_ENABLED", "true")=="true",
    "jd_match": os.getenv("AI_JD_MATCH_ENABLED", "false")=="true"  # start false
}
