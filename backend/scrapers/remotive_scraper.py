"""
Remotive.com API Scraper
Fetches real remote software development jobs from the free Remotive API.
No API key required.
"""
import httpx
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate


def scrape_remotive_jobs() -> List[JobCreate]:
    """Fetch software dev jobs from Remotive's free public API."""
    jobs: List[JobCreate] = []
    
    url = "https://remotive.com/api/remote-jobs"
    params = {"category": "software-dev", "limit": 250}
    
    try:
        resp = httpx.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Remotive] Error fetching jobs: {e}")
        return jobs
    
    for item in data.get("jobs", []):
        title = (item.get("title") or "").strip()
        company = (item.get("company_name") or "Unknown").strip()
        location = (item.get("candidate_required_location") or "Remote").strip()
        description = (item.get("description") or "").strip()
        job_url = (item.get("url") or "").strip()
        salary = (item.get("salary") or "").strip() or None
        tags_raw = item.get("tags") or []
        
        if not title or not job_url:
            continue
        
        # Strip HTML from description
        import re
        description_clean = re.sub(r'<[^>]+>', ' ', description)
        description_clean = re.sub(r'\s+', ' ', description_clean).strip()
        # Truncate to 5000 chars for better search & AI matching
        if len(description_clean) > 5000:
            description_clean = description_clean[:4997] + "..."
        
        # Infer job type from title
        title_lower = title.lower()
        job_type = "Full-time"
        if "intern" in title_lower:
            job_type = "Internship"
        elif "new grad" in title_lower or "junior" in title_lower or "entry" in title_lower or "jr" in title_lower:
            job_type = "New Grad"
        elif "contract" in title_lower or "freelance" in title_lower:
            job_type = "Contract"
        
        jobs.append(JobCreate(
            title=title[:250],
            company=company[:250],
            location=location[:250] if location else None,
            remote=True,  # Remotive is all remote
            description=description_clean,
            url=job_url,
            source="Remotive",
            salary=salary,
            job_type=job_type,
            tags=tags_raw[:10] if tags_raw else None,
        ))
    
    return jobs


if __name__ == "__main__":
    results = scrape_remotive_jobs()
    print(f"Found {len(results)} jobs from Remotive")
    for j in results[:5]:
        print(f"  - {j.title} @ {j.company} [{j.location}]")
