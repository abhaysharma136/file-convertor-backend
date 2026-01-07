from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.cleanup import start_cleanup_worker
from api.convert import router as convert_router
from api.resume import router as resume_router
from api.match import router as match_router
from api.status import router as status_router



app = FastAPI()
start_cleanup_worker()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(convert_router)
app.include_router(resume_router)
app.include_router(match_router)
app.include_router(status_router)
