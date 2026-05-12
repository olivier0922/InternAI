"""
Jobicy.com API Scraper
Fetches remote tech job listings from the free Jobicy API.
No API key required.
"""
import httpx
import os
import re
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate


def scrape_jobicy_jobs() -> List[JobCreate]:
    """Fetch remote tech jobs from Jobicy's free public API."""
    jobs: List[JobCreate] = []

    max_pages = int(os.getenv("JOBICY_MAX_PAGES", "20"))
    page_size = int(os.getenv("JOBICY_PAGE_SIZE", "20"))
    jobicy_tag = os.getenv("JOBICY_TAG", "engineering").strip()

    # Paginate to get more results
    for page_num in range(1, max_pages + 1):
        url = "https://jobicy.com/api/v2/remote-jobs"
        params = {
            "count": page_size,
            "page": page_num,
        }
        if jobicy_tag:
            params["tag"] = jobicy_tag

        try:
            resp = httpx.get(url, params=params, timeout=30, headers={
                "Accept": "application/json",
                "User-Agent": "InternAI-JobBot/2.0 (student project)"
            })
            if resp.status_code != 200:
                print(f"[Jobicy] Error fetching jobs (page {page_num}): {resp.status_code}")
                if resp.status_code in (400, 401, 403, 429):
                    break
                continue
            data = resp.json()
        except Exception as e:
            print(f"[Jobicy] Error fetching jobs (page {page_num}): {e}")
            continue

        page_jobs = data.get("jobs", [])
        if not page_jobs:
            break

        for item in page_jobs:
            title = (item.get("jobTitle") or "").strip()
            company = (item.get("companyName") or "Unknown").strip()
            location = (item.get("jobGeo") or "Remote").strip()
            description = (item.get("jobDescription") or "").strip()
            job_url = (item.get("url") or "").strip()
            salary_min = item.get("annualSalaryMin")
            salary_max = item.get("annualSalaryMax")
            salary_currency = item.get("salaryCurrency") or "USD"
            job_industry = item.get("jobIndustry") or []
            job_level = (item.get("jobLevel") or "").strip()

            if not title or not job_url:
                continue

            # Build salary string
            salary = None
            if salary_min and salary_max:
                salary = f"{salary_currency} {salary_min:,}–{salary_max:,}/yr"
            elif salary_min:
                salary = f"{salary_currency} {salary_min:,}+/yr"

            # Strip HTML from description
            description_clean = re.sub(r'<[^>]+>', ' ', description)
            description_clean = re.sub(r'\s+', ' ', description_clean).strip()
            if len(description_clean) > 5000:
                description_clean = description_clean[:4997] + "..."

            # Infer job type
            title_lower = title.lower()
            level_lower = job_level.lower()
            job_type = "Full-time"
            if "intern" in title_lower or "intern" in level_lower:
                job_type = "Internship"
            elif any(kw in title_lower for kw in ["junior", "jr", "new grad", "entry", "graduate"]):
                job_type = "New Grad"
            elif "contract" in title_lower or "freelance" in title_lower:
                job_type = "Contract"

            # Build tags from industry
            tags = []
            if isinstance(job_industry, list):
                tags = [ind.strip() for ind in job_industry if isinstance(ind, str)][:10]

            jobs.append(JobCreate(
                title=title[:250],
                company=company[:250],
                location=location[:250] if location else None,
                remote=True,  # Jobicy is remote-focused
                description=description_clean if description_clean else title,
                url=job_url,
                source="Jobicy",
                salary=salary,
                job_type=job_type,
                tags=tags if tags else None,
            ))

    return jobs


if __name__ == "__main__":
    results = scrape_jobicy_jobs()
    print(f"Found {len(results)} jobs from Jobicy")
    for j in results[:5]:
        print(f"  - {j.title} @ {j.company} [{j.location}] | {j.salary or 'No salary'}")
