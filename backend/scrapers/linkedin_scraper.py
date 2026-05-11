"""
LinkedIn Jobs Scraper (via Scrapling StealthyFetcher)
Scrapes LinkedIn's public guest job search pages for multiple queries.
No login required — uses LinkedIn's public job listing pages.
"""
import re
import time
import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate

# Helper: safe first element from Scrapling selector
def _first(selectors):
    """Get first element from Scrapling Selectors, or None."""
    try:
        return selectors.first if selectors and len(selectors) > 0 else None
    except Exception:
        return None

# Search queries to run
SEARCH_QUERIES = [
    # ── Montreal General ──
    ("software engineer", "Montreal, QC"),
    ("developer", "Montreal, QC"),
    ("data scientist", "Montreal, QC"),
    ("devops", "Montreal, QC"),
    ("machine learning", "Montreal, QC"),
    ("frontend developer", "Montreal, QC"),
    ("backend developer", "Montreal, QC"),
    ("python developer", "Montreal, QC"),
    ("java developer", "Montreal, QC"),
    ("react developer", "Montreal, QC"),
    ("cloud engineer", "Montreal, QC"),
    ("QA engineer", "Montreal, QC"),
    ("data engineer", "Montreal, QC"),
    ("full stack developer", "Montreal, QC"),
    ("web developer", "Montreal, QC"),
    ("AI engineer", "Montreal, QC"),
    ("product manager", "Montreal, QC"),

    # ── Montreal Intern Queries ──
    ("intern", "Montreal, QC"),
    ("stage", "Montreal, QC"),
    ("stagiaire", "Montreal, QC"),
    ("co-op", "Montreal, QC"),
    ("summer intern", "Montreal, QC"),
    ("software intern", "Montreal, QC"),
    ("software engineering intern", "Montreal, QC"),
    ("data intern", "Montreal, QC"),
    ("stagiaire informatique", "Montreal, QC"),
    ("frontend intern", "Montreal, QC"),
    ("backend intern", "Montreal, QC"),

    # ── Toronto ──
    ("software engineer", "Toronto, ON"),
    ("developer", "Toronto, ON"),
    ("software intern", "Toronto, ON"),
    ("data scientist", "Toronto, ON"),
    ("frontend developer", "Toronto, ON"),
    ("backend developer", "Toronto, ON"),
    ("full stack developer", "Toronto, ON"),
    ("devops", "Toronto, ON"),
    ("machine learning", "Toronto, ON"),
    ("intern", "Toronto, ON"),

    # ── Vancouver ──
    ("software engineer", "Vancouver, BC"),
    ("developer", "Vancouver, BC"),
    ("software intern", "Vancouver, BC"),
    ("data scientist", "Vancouver, BC"),

    # ── Ottawa ──
    ("software engineer", "Ottawa, ON"),
    ("developer", "Ottawa, ON"),
    ("software intern", "Ottawa, ON"),

    # ── Canada-wide ──
    ("software engineer", "Canada"),
    ("python developer", "Canada"),
    ("react developer", "Canada"),
    ("full stack developer", "Canada"),
    ("intern software", "Canada"),
    ("data engineer", "Canada"),
    ("machine learning", "Canada"),
    ("cloud engineer", "Canada"),
    ("devops", "Canada"),

    # ── US Major Cities ──
    ("software engineer", "New York, NY"),
    ("developer", "New York, NY"),
    ("software intern", "New York, NY"),
    ("software engineer", "San Francisco, CA"),
    ("developer", "San Francisco, CA"),
    ("software intern", "San Francisco, CA"),
    ("software engineer", "Seattle, WA"),
    ("developer", "Seattle, WA"),
    ("software engineer", "Austin, TX"),
    ("software engineer", "Chicago, IL"),
    ("software engineer", "Boston, MA"),
    ("software engineer", "Los Angeles, CA"),

    # ── Global/Remote ──
    ("software engineer intern", ""),
    ("frontend developer", "Remote"),
    ("backend developer", "Remote"),
    ("data engineer", "Remote"),
    ("software engineer", "Remote"),
    ("full stack developer", "Remote"),
    ("machine learning engineer", "Remote"),
    ("devops engineer", "Remote"),
    ("python developer", "Remote"),
]

def scrape_linkedin_jobs(dynamic_skills: List[str] = None) -> List[JobCreate]:
    """Scrape LinkedIn public job listings using Scrapling's StealthyFetcher."""
    
    queries = list(SEARCH_QUERIES)
    if dynamic_skills:
        for skill in dynamic_skills[:3]:
            queries.insert(0, (f"{skill} developer", "Montreal, QC"))
            queries.insert(0, (f"{skill} engineer", "Canada"))
            
    try:
        from scrapling.fetchers import StealthyFetcher
    except ImportError:
        print("[LinkedIn] scrapling not installed. Run: pip install 'scrapling[fetchers]' && scrapling install")
        return []

    jobs: List[JobCreate] = []
    seen_urls = set()

    for keywords, location in queries:
        # Scale up to 10 pages (250 jobs per query)
        for start_idx in range(0, 100, 25):
            try:
                kw = keywords.replace(' ', '%20')
                loc = location.replace(' ', '%20').replace(',', '%2C')
                # Add delay to avoid immediate blocking from heavy pagination
                if start_idx > 0:
                    time.sleep(2.5)
                full_url = f"https://www.linkedin.com/jobs/search/?keywords={kw}&location={loc}&f_TPR=r604800&start={start_idx}"
                print(f"  [LinkedIn] Searching: '{keywords}' in '{location}' (start={start_idx})...")

                page = StealthyFetcher.fetch(full_url, headless=True, network_idle=True)

                if page.status != 200:
                    print(f"  [LinkedIn] Got status {page.status}")
                    continue

                job_cards = page.css('div.base-card')
                if not job_cards or len(job_cards) == 0:
                    job_cards = page.css('.base-search-card')
                if not job_cards or len(job_cards) == 0:
                    job_cards = page.css('.job-search-card')

                print(f"  [LinkedIn] Found {len(job_cards)} cards")
                if len(job_cards) == 0:
                    break # no more pages

                for card in job_cards:
                    try:
                        title_el = _first(card.css('h3.base-search-card__title')) or _first(card.css('h3')) or _first(card.css('.base-search-card__title'))
                        title = title_el.text.strip() if title_el else None

                        company_el = _first(card.css('a.hidden-nested-link')) or _first(card.css('h4.base-search-card__subtitle'))
                        if company_el:
                            company = company_el.text.strip() or company_el.get_all_text().strip()
                        else:
                            company = "Unknown"

                        location_el = _first(card.css('span.job-search-card__location')) or _first(card.css('.base-search-card__metadata'))
                        job_loc = location_el.text.strip() if location_el else location

                        link_el = _first(card.css('a.base-card__full-link')) or _first(card.css('a'))
                        job_url = link_el.attrib.get('href', '') if link_el else ''
                        if '?' in job_url:
                            job_url = job_url.split('?')[0]

                        if not title or not job_url or job_url in seen_urls:
                            continue
                        seen_urls.add(job_url)

                        combined = f"{title} {job_loc}".lower()
                        remote = "remote" in combined or "télétravail" in combined

                        title_lower = title.lower()
                        job_type = "Full-time"
                        if any(kw in title_lower for kw in ["intern", "stage", "stagiaire", "internship"]):
                            job_type = "Internship"
                        elif any(kw in title_lower for kw in ["junior", "jr", "new grad", "entry level", "graduate"]):
                            job_type = "New Grad"
                        elif "contract" in title_lower or "freelance" in title_lower:
                            job_type = "Contract"

                        desc_el = _first(card.css('.base-search-card__snippet'))
                        description = desc_el.text.strip() if desc_el else f"{title} at {company}"

                        jobs.append(JobCreate(
                            title=title[:250],
                            company=company[:250],
                            location=job_loc[:250] if job_loc else None,
                            remote=remote,
                            description=description[:5000],
                            url=job_url,
                            source="LinkedIn",
                            job_type=job_type,
                        ))
                    except Exception:
                        continue

                time.sleep(2)
            except Exception as e:
                print(f"  [LinkedIn] Error during scraping '{keywords}': {e}")
                
        time.sleep(1.5)

    return jobs

if __name__ == "__main__":
    jobs = scrape_linkedin_jobs(["react"])
    print(f"Found {len(jobs)} jobs")
    if jobs:
        print(jobs[0].dict())
