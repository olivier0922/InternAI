"""
The Muse API Scraper
Fetches real engineering/tech jobs from The Muse's free public API.
No API key required for <500 requests/hour.
"""
import httpx
import re
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate


CATEGORIES = [
    "Engineering",
    "Data Science",
    "IT",
    "Design and UX",
    "Data and Analytics",
]


def scrape_themuse_jobs() -> List[JobCreate]:
    """Fetch engineering/tech jobs from The Muse's free public API (paginated, multi-category)."""
    jobs: List[JobCreate] = []
    seen_urls = set()

    for category in CATEGORIES:
        for page in range(0, 5):  # Up to 5 pages per category
            url = "https://www.themuse.com/api/public/jobs"
            params = {
                "category": category,
                "page": page,
            }

            try:
                resp = httpx.get(url, params=params, timeout=30, headers={
                    "Accept": "application/json",
                    "User-Agent": "InternAI-JobBot/2.0 (student project)"
                })
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"[The Muse] Error fetching {category} page {page}: {e}")
                continue

            results = data.get("results", [])
            if not results:
                break  # No more pages

            for item in results:
                title = (item.get("name") or "").strip()
                company_data = item.get("company") or {}
                company = (company_data.get("name") or "Unknown").strip()
                locations = item.get("locations") or []
                location_str = ", ".join(
                    (loc.get("name") or "") for loc in locations
                ).strip() or None
                description = (item.get("contents") or "").strip()
                job_url = f"https://www.themuse.com/jobs/{item.get('short_name', item.get('id', ''))}"

                # Use the refs landing_page if available
                refs = item.get("refs") or {}
                if refs.get("landing_page"):
                    job_url = refs["landing_page"]

                if not title or not job_url or job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                # Strip HTML from description
                description_clean = re.sub(r'<[^>]+>', ' ', description)
                description_clean = re.sub(r'\s+', ' ', description_clean).strip()
                if len(description_clean) > 5000:
                    description_clean = description_clean[:4997] + "..."

                # Determine remote
                remote = False
                if location_str:
                    loc_lower = location_str.lower()
                    remote = "remote" in loc_lower or "flexible" in loc_lower or "anywhere" in loc_lower

                # Infer job type
                title_lower = title.lower()
                levels = item.get("levels") or []
                level_names = [lv.get("short_name", "").lower() for lv in levels]
                
                job_type = "Full-time"
                if "intern" in title_lower or "internship" in " ".join(level_names):
                    job_type = "Internship"
                elif any(kw in title_lower for kw in ["junior", "jr", "new grad", "entry level", "graduate"]):
                    job_type = "New Grad"
                elif "entry" in " ".join(level_names):
                    job_type = "New Grad"
                elif "contract" in title_lower or "freelance" in title_lower:
                    job_type = "Contract"

                # Tags from category and levels
                tags = [category]
                tags.extend([lv.get("name", "") for lv in levels if lv.get("name")])
                tags = [t for t in tags if t][:10]

                jobs.append(JobCreate(
                    title=title[:250],
                    company=company[:250],
                    location=location_str[:250] if location_str else None,
                    remote=remote,
                    description=description_clean if description_clean else title,
                    url=job_url,
                    source="The Muse",
                    salary=None,  # The Muse doesn't expose salary in API
                    job_type=job_type,
                    tags=tags if tags else None,
                ))

    return jobs


if __name__ == "__main__":
    results = scrape_themuse_jobs()
    print(f"Found {len(results)} jobs from The Muse")
    for j in results[:10]:
        print(f"  - {j.title} @ {j.company} [{j.location}] ({j.job_type})")
