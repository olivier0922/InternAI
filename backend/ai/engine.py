import os
from groq import Groq
import instructor
from pydantic import BaseModel, Field
from typing import List

groq_api_key = os.environ.get("GROQ_API_KEY", "")
client = instructor.patch(Groq(api_key=groq_api_key)) if groq_api_key else None

class MatchResult(BaseModel):
    score: int = Field(..., description="Match score from 0 to 100", ge=0, le=100)
    matching_skills: List[str] = Field(..., description="List of matching skills")
    missing_skills: List[str] = Field(..., description="List of missing skills required by the job")
    explanation: str = Field(..., description="Short 1-2 sentence explanation of the match")

class ExtractedResume(BaseModel):
    skills: List[str] = Field(..., description="List of technical skills found in the resume")
    experience_years: int = Field(0, description="Estimated years of experience")

def extract_resume_info(resume_text: str) -> ExtractedResume:
    if not client:
        return ExtractedResume(skills=[], experience_years=0)
        
    return client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_model=ExtractedResume,
        messages=[
            {"role": "system", "content": "You are an expert technical recruiter AI. Extract the technical skills and years of experience from the resume text."},
            {"role": "user", "content": f"Resume Text:\n{resume_text}"}
        ]
    )

def match_job(resume_text: str, job_description: str) -> MatchResult:
    if not client:
        return MatchResult(score=0, matching_skills=[], missing_skills=[], explanation="AI not configured.")
        
    return client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_model=MatchResult,
        messages=[
            {"role": "system", "content": "You are an AI matching engine. Compare the candidate's resume with the job description and output a strict JSON evaluation."},
            {"role": "user", "content": f"Resume:\n{resume_text}\n\nJob Description:\n{job_description}"}
        ]
    )
