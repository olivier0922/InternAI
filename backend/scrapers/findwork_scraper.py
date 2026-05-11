"""
FindWork.dev API Scraper
Fetches real software engineering jobs from the free FindWork API.
No API key required for basic access.
"""
import httpx
from typing import List
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate


def scrape_findwork_jobs() -> List[JobCreate]:
    """Fetch software jobs from FindWork.dev free API."""
    jobs: List[JobCreate] = []
    
    url = "https://findwork.dev/api/jobs/"
    
    try:
        resp = httpx.get(url, timeout=30, headers={
            "Accept": "application/json",
            "User-Agent": "InternAI-JobBot/1.0"
        })
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[FindWork] Error fetching: {e}")
        return jobs
    
    for item in data.get("results", []):
        title = (item.get("role") or "").strip()
        company = (item.get("company_name") or "Unknown").strip()
        location = (item.get("location") or "").strip()
        description = (item.get("text") or "").strip()
        job_url = (item.get("url") or "").strip()
        remote = item.get("remote", False)
        keywords = item.get("keywords") or []
        
        if not title or not job_url:
            continue
        
        # Clean HTML from description
        description_clean = re.sub(r'<[^>]+>', ' ', description)
        description_clean = re.sub(r'\s+', ' ', description_clean).strip()
        if len(description_clean) > 5000:
            description_clean = description_clean[:4997] + "..."
        
        # Infer job type
        title_lower = title.lower()
        job_type = "Full-time"
        if "intern" in title_lower:
            job_type = "Internship"
        elif any(kw in title_lower for kw in ["junior", "jr", "new grad", "entry level", "graduate"]):
            job_type = "New Grad"
        elif "contract" in title_lower or "freelance" in title_lower:
            job_type = "Contract"
        
        jobs.append(JobCreate(
            title=title[:250],
            company=company[:250],
            location=location[:250] if location else None,
            remote=bool(remote),
            description=description_clean if description_clean else title,
            url=job_url,
            source="FindWork",
            job_type=job_type,
            tags=keywords[:10] if keywords else None,
        ))
    
    return jobs


if __name__ == "__main__":
    results = scrape_findwork_jobs()
    print(f"Found {len(results)} jobs from FindWork.dev")
    for j in results[:5]:
        print(f"  - {j.title} @ {j.company} [{j.location}]")
