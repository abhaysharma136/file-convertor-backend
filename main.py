from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.cleanup import start_cleanup_worker
from api.convert import router as convert_router
from api.resume import router as resume_router
from api.match import router as match_router
from api.status import router as status_router
from api.usage import router as usage_router
from api.admin import router as admin_router
from core.middleware import logging_middleware
import os
from datetime import datetime

app = FastAPI()
@app.on_event("startup")
def start_background_workers():
    start_cleanup_worker()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://applyra.in","https://www.applyra.in","https://file-convertor-frontend-ywt8.vercel.app"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(logging_middleware)

app.include_router(convert_router)
app.include_router(resume_router)
app.include_router(match_router)
app.include_router(status_router)
app.include_router(usage_router)
app.include_router(admin_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "applyra-backend",
        "environment": os.getenv("ENV", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
def root():
    return {
        "message": "Applyra API is running",
        "docs": "/docs"
    }
