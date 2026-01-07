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