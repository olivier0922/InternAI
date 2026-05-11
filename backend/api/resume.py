from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from utils.parser import extract_text_from_file
from ai.engine import extract_resume_info
from utils.auth import get_current_user, User, supabase
import uuid

router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/upload")
def upload_resume(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(400, "Only PDF and DOCX are supported")
        
    contents = file.file.read()
    
    try:
        parsed_text = extract_text_from_file(file.filename, contents)
    except Exception as e:
        raise HTTPException(400, f"Error parsing file: {str(e)}")
        
    extracted_info = extract_resume_info(parsed_text)
    
    if supabase:
        file_path = f"{user.id}/{uuid.uuid4()}_{file.filename}"
        supabase.storage.from_("resumes").upload(file_path, contents)
        file_url = supabase.storage.from_("resumes").get_public_url(file_path)
        
        supabase.table("resumes").insert({
            "user_id": user.id,
            "file_url": file_url,
            "parsed_text": parsed_text,
            "extracted_skills": extracted_info.skills
        }).execute()
        
    return {
        "message": "Resume uploaded successfully", 
        "skills": extracted_info.skills
    }

@router.get("/me")
def get_my_resumes(user: User = Depends(get_current_user)):
    if not supabase:
        return []
    response = supabase.table("resumes").select("*").eq("user_id", user.id).order("uploaded_at", desc=True).execute()
    return response.data
