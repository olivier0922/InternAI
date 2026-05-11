"""
Himalayas.app API Scraper
Fetches remote-first tech job listings from the free Himalayas API.
No API key required.
"""
import httpx
import re
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate


def scrape_himalayas_jobs() -> List[JobCreate]:
    """Fetch remote tech jobs from Himalayas.app free public API."""
    jobs: List[JobCreate] = []

    # Paginate to get more results
    for offset in range(0, 500, 100):
        url = "https://himalayas.app/jobs/api"
        params = {
            "limit": 100,
            "offset": offset,
        }

        try:
            resp = httpx.get(url, params=params, timeout=30, headers={
                "Accept": "application/json",
                "User-Agent": "InternAI-JobBot/2.0 (student project)"
            })
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[Himalayas] Error fetching jobs (offset={offset}): {e}")
            continue

        page_jobs = data.get("jobs", [])
        if not page_jobs:
            break  # No more results

        for item in page_jobs:
            title = (item.get("title") or "").strip()
            company = (item.get("companyName") or "Unknown").strip()
            # Location from locationRestrictions array
            loc_restrictions = item.get("locationRestrictions") or []
            location = ", ".join(loc_restrictions) if loc_restrictions else "Remote"
            description = (item.get("description") or "").strip()
            job_url = (item.get("applicationLink") or item.get("guid") or "").strip()
            salary_min = item.get("minSalary")
            salary_max = item.get("maxSalary")
            salary_currency = item.get("currency") or "USD"
            categories = item.get("categories") or []
            # seniority is a list in the API
            seniority_raw = item.get("seniority") or []
            experience_level = seniority_raw[0] if isinstance(seniority_raw, list) and seniority_raw else ""
            if isinstance(experience_level, str):
                experience_level = experience_level.strip()
            else:
                experience_level = ""

            if not title or not job_url:
                continue

            # Build salary string
            salary = None
            if salary_min and salary_max:
                try:
                    salary = f"{salary_currency} {int(salary_min):,}–{int(salary_max):,}/yr"
                except (ValueError, TypeError):
                    pass
            elif salary_min:
                try:
                    salary = f"{salary_currency} {int(salary_min):,}+/yr"
                except (ValueError, TypeError):
                    pass

            # Strip HTML from description
            description_clean = re.sub(r'<[^>]+>', ' ', description)
            description_clean = re.sub(r'\s+', ' ', description_clean).strip()
            if len(description_clean) > 5000:
                description_clean = description_clean[:4997] + "..."

            # Infer job type
            title_lower = title.lower()
            exp_lower = experience_level.lower()
            job_type = "Full-time"
            if "intern" in title_lower or "intern" in exp_lower:
                job_type = "Internship"
            elif any(kw in title_lower for kw in ["junior", "jr", "new grad", "entry", "graduate"]):
                job_type = "New Grad"
            elif "entry" in exp_lower:
                job_type = "New Grad"
            elif "contract" in title_lower or "freelance" in title_lower:
                job_type = "Contract"

            # Build tags
            tags = []
            if isinstance(categories, list):
                for cat in categories[:10]:
                    if isinstance(cat, str):
                        tags.append(cat.strip())
                    elif isinstance(cat, dict):
                        tags.append(cat.get("name", "").strip())

            jobs.append(JobCreate(
                title=title[:250],
                company=company[:250],
                location=location[:250] if location else None,
                remote=True,  # Himalayas is remote-focused
                description=description_clean if description_clean else title,
                url=job_url,
                source="Himalayas",
                salary=salary,
                job_type=job_type,
                tags=[t for t in tags if t][:10] or None,
            ))

    return jobs


if __name__ == "__main__":
    results = scrape_himalayas_jobs()
    print(f"Found {len(results)} jobs from Himalayas")
    for j in results[:5]:
        print(f"  - {j.title} @ {j.company} [{j.location}] | {j.salary or 'No salary'}")
