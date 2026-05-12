"""
Hacker News Jobs Scraper (Algolia API)
Fetches real job postings from HN using the free Algolia search API.
No API key or browser required — pure HTTP.
"""
import httpx
import os
import re
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate


def scrape_hn_jobs() -> List[JobCreate]:
    """Fetch job postings from Hacker News via the Algolia API (no Playwright needed)."""
    jobs: List[JobCreate] = []

    max_pages = int(os.getenv("HN_MAX_PAGES", "10"))

    # Algolia HN API — search for recent job stories, paginate
    for page_num in range(0, max_pages):
        url = "https://hn.algolia.com/api/v1/search_by_date"
        params = {
            "tags": "job",
            "hitsPerPage": 200,
            "page": page_num,
        }

        try:
            resp = httpx.get(url, params=params, timeout=30, headers={
                "User-Agent": "InternAI-JobBot/2.0 (student project)"
            })
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[HN] Error fetching jobs (page {page_num}): {e}")
            continue

        hits = data.get("hits", [])
        if not hits:
            break

        for item in hits:
            full_title = (item.get("title") or "").strip()
            story_text = (item.get("story_text") or "").strip()
            story_url = item.get("url") or ""
            story_id = item.get("objectID") or ""

            if not full_title:
                continue

            # Build the URL
            job_url = story_url if story_url else f"https://news.ycombinator.com/item?id={story_id}"

            # Parse "Company (YC Batch) is hiring..." format
            company = "Unknown"
            role = full_title

            # Common patterns: "Company is hiring" or "Company (YC S23) Is Hiring"
            hiring_patterns = [
                r'^(.+?)\s+\(YC\s+[A-Z]\d+\)\s+[Ii]s\s+[Hh]iring\s*(.*)',
                r'^(.+?)\s+[Ii]s\s+[Hh]iring\s*(.*)',
            ]

            for pattern in hiring_patterns:
                match = re.match(pattern, full_title)
                if match:
                    company = match.group(1).strip()
                    role = match.group(2).strip() or full_title
                    break

            # Strip HTML from story_text
            description = re.sub(r'<[^>]+>', ' ', story_text) if story_text else full_title
            description = re.sub(r'\s+', ' ', description).strip()
            if len(description) > 5000:
                description = description[:4997] + "..."

            # Determine remote
            text_lower = (full_title + " " + description).lower()
            remote = "remote" in text_lower

            # Infer location from text
            location = "Remote" if remote else None

            # Infer job type
            title_lower = full_title.lower()
            job_type = "Full-time"
            if "intern" in title_lower:
                job_type = "Internship"
            elif any(kw in title_lower for kw in ["junior", "jr", "new grad", "entry"]):
                job_type = "New Grad"
            elif "contract" in title_lower or "freelance" in title_lower:
                job_type = "Contract"

            jobs.append(JobCreate(
                title=role[:250] if role else full_title[:250],
                company=company[:250],
                location=location,
                remote=remote,
                description=description if description else full_title,
                url=job_url,
                source="Hacker News",
                job_type=job_type,
            ))

    return jobs


if __name__ == "__main__":
    results = scrape_hn_jobs()
    print(f"Found {len(results)} jobs from Hacker News")
    for j in results[:10]:
        print(f"  - {j.title} @ {j.company} [{j.location}]")
