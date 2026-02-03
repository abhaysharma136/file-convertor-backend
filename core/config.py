import os

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

MAX_AI_TOKENS_PER_JOB = 2500
MAX_AI_CALLS_PER_DAY = 500

AI_ENABLED = {
    "resume_analyzer": True,
    "jd_match": False  # start false
}
