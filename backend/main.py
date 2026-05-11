from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="InternAI API",
    description="Backend API for InternAI - Job & Resume Discovery Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://olivier0922.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

from api import jobs, resume, ai
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(resume.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
