from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    remote: bool = False
    description: str
    salary: Optional[str] = None
    url: str
    source: str
    job_type: Optional[str] = None  # "Internship", "Full-time", "New Grad", "Contract"
    tags: Optional[List[str]] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
