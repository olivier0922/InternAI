from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ai.engine import match_job, MatchResult
from utils.auth import get_current_user, User, supabase

router = APIRouter(prefix="/ai", tags=["AI"])

class MatchRequest(BaseModel):
    job_id: str

@router.post("/match", response_model=MatchResult)
def generate_match(request: MatchRequest, user: User = Depends(get_current_user)):
    if not supabase:
        raise HTTPException(500, "Database not connected")
        
    resumes = supabase.table("resumes").select("parsed_text").eq("user_id", user.id).order("uploaded_at", desc=True).limit(1).execute()
    if not resumes.data:
        raise HTTPException(404, "No resume found. Please upload a resume first.")
        
    resume_text = resumes.data[0]["parsed_text"]
    
    job = supabase.table("jobs").select("description").eq("id", request.job_id).single().execute()
    if not job.data:
        raise HTTPException(404, "Job not found")
        
    job_desc = job.data["description"]
    
    result = match_job(resume_text, job_desc)
    
    existing = supabase.table("matches").select("id").eq("user_id", user.id).eq("job_id", request.job_id).execute()
    if not existing.data:
        supabase.table("matches").insert({
            "user_id": user.id,
            "job_id": request.job_id,
            "score": result.score,
            "matching_skills": result.matching_skills,
            "missing_skills": result.missing_skills,
            "explanation": result.explanation
        }).execute()
    else:
        supabase.table("matches").update({
            "score": result.score,
            "matching_skills": result.matching_skills,
            "missing_skills": result.missing_skills,
            "explanation": result.explanation
        }).eq("user_id", user.id).eq("job_id", request.job_id).execute()
        
    return result
