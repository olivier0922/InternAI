"""
Arbeitnow.com API Scraper
Fetches real job listings from the free Arbeitnow Job Board API.
No API key required.
"""
import httpx
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate


def scrape_arbeitnow_jobs() -> List[JobCreate]:
    """Fetch software/engineering jobs from Arbeitnow's free API (multiple pages)."""
    jobs: List[JobCreate] = []
    
    # Fetch up to 25 pages
    for page in range(1, 26):
        url = f"https://www.arbeitnow.com/api/job-board-api?page={page}"
        
        try:
            resp = httpx.get(url, timeout=30, headers={"Accept": "application/json"})
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[Arbeitnow] Error fetching page {page}: {e}")
            continue
        
        for item in data.get("data", []):
            title = (item.get("title") or "").strip()
            company = (item.get("company_name") or "Unknown").strip()
            location = (item.get("location") or "").strip()
            description = (item.get("description") or "").strip()
            job_url = (item.get("url") or "").strip()
            remote = item.get("remote", False)
            tags_raw = item.get("tags") or []
            
            if not title or not job_url:
                continue
            
            # Filter for software/engineering/tech roles
            title_lower = title.lower()
            tech_keywords = [
                "software", "developer", "engineer", "frontend", "backend",
                "full stack", "fullstack", "devops", "data", "machine learning",
                "python", "java", "react", "node", "cloud", "intern", "sre",
                "infrastructure", "platform", "mobile", "ios", "android",
                "web", "api", "security", "qa", "test", "automation",
                "ai", "ml", "deep learning", "nlp", "computer", "system",
                "typescript", "golang", "rust", "c++", "kubernetes", "docker",
                "architect", "analyst", "admin", "network", "database", "sql",
                "linux", "php", "ruby", "scala", "swift", "kotlin", "flutter",
                "tech", "it ", "ops", "scrum", "agile", "product", "ux", "ui",
                "design", "embedded", "firmware", "robotics", "blockchain",
                "crypto", "fintech", "cyber", "gaming", "game"
            ]
            
            # Check title AND tags for tech keywords (broader filter)
            tags_lower = " ".join(t.lower() for t in tags_raw) if tags_raw else ""
            combined = title_lower + " " + tags_lower
            if not any(kw in combined for kw in tech_keywords):
                continue
            
            # Strip HTML from description
            import re
            description_clean = re.sub(r'<[^>]+>', ' ', description)
            description_clean = re.sub(r'\s+', ' ', description_clean).strip()
            if len(description_clean) > 5000:
                description_clean = description_clean[:4997] + "..."
            
            # Infer job type
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
                remote=bool(remote),
                description=description_clean,
                url=job_url,
                source="Arbeitnow",
                job_type=job_type,
                tags=tags_raw[:10] if tags_raw else None,
            ))
        
        # If no more pages
        if not data.get("links", {}).get("next"):
            break
    
    return jobs


if __name__ == "__main__":
    results = scrape_arbeitnow_jobs()
    print(f"Found {len(results)} tech jobs from Arbeitnow")
    for j in results[:5]:
        print(f"  - {j.title} @ {j.company} [{j.location}]")
