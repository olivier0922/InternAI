from fastapi import APIRouter, Query
from typing import List, Optional
from schemas.job import JobResponse
from utils.auth import supabase
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=List[JobResponse])
def get_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    remote_only: bool = Query(False),
    search: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    date_posted: Optional[str] = Query(None, description="Filter by date: 24h, 7d, 30d"),
    sources: Optional[str] = Query(None, description="Comma-separated source names"),
    sort_by: Optional[str] = Query("date", description="Sort by: date or relevance"),
):
    if not supabase:
        return []

    query = supabase.table("jobs").select("*", count="exact").order("created_at", desc=True)
    
    if remote_only:
        query = query.eq("remote", True)
    
    # Multi-field search: search across title, company, description, and tags
    if search:
        search_term = search.strip()
        # Use Supabase's or_() to search across multiple columns
        query = query.or_(
            f"title.ilike.%{search_term}%,"
            f"company.ilike.%{search_term}%,"
            f"description.ilike.%{search_term}%"
        )
    
    if location:
        query = query.ilike("location", f"%{location}%")
    
    if company:
        query = query.ilike("company", f"%{company}%")
    
    if job_type:
        query = query.eq("job_type", job_type)
    
    # Date filter
    if date_posted:
        now = datetime.now(timezone.utc)
        if date_posted == "24h":
            cutoff = now - timedelta(hours=24)
        elif date_posted == "7d":
            cutoff = now - timedelta(days=7)
        elif date_posted == "30d":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = None
        
        if cutoff:
            query = query.gte("created_at", cutoff.isoformat())
    
    # Source filter
    if sources:
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
        if source_list:
            query = query.in_("source", source_list)
    
    query = query.range(offset, offset + limit - 1)
    response = query.execute()
    return response.data

@router.get("/count")
def get_jobs_count(
    search: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    remote_only: bool = Query(False),
    date_posted: Optional[str] = Query(None),
    sources: Optional[str] = Query(None),
):
    """Get total count of jobs matching filters."""
    if not supabase:
        return {"count": 0}
    
    query = supabase.table("jobs").select("id", count="exact")
    
    if remote_only:
        query = query.eq("remote", True)
    if search:
        search_term = search.strip()
        query = query.or_(
            f"title.ilike.%{search_term}%,"
            f"company.ilike.%{search_term}%,"
            f"description.ilike.%{search_term}%"
        )
    if location:
        query = query.ilike("location", f"%{location}%")
    if job_type:
        query = query.eq("job_type", job_type)
    
    if date_posted:
        now = datetime.now(timezone.utc)
        cutoff_map = {"24h": timedelta(hours=24), "7d": timedelta(days=7), "30d": timedelta(days=30)}
        if date_posted in cutoff_map:
            query = query.gte("created_at", (now - cutoff_map[date_posted]).isoformat())
    
    if sources:
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
        if source_list:
            query = query.in_("source", source_list)
    
    response = query.execute()
    return {"count": response.count or len(response.data)}

@router.get("/sources")
def get_job_sources():
    """Get list of available job sources and their counts."""
    if not supabase:
        return {"sources": []}
    
    # Fetch all unique sources
    response = supabase.table("jobs").select("source").execute()
    source_counts = {}
    for row in response.data:
        src = row.get("source", "Unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
    
    return {
        "sources": [
            {"name": name, "count": count}
            for name, count in sorted(source_counts.items(), key=lambda x: -x[1])
        ],
        "total": sum(source_counts.values()),
    }

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    if not supabase:
        return None
    response = supabase.table("jobs").select("*").eq("id", job_id).single().execute()
    return response.data
