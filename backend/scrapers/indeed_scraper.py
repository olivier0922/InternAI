"""
Indeed Jobs Scraper (via Scrapling StealthyFetcher)
Scrapes Indeed's public job search pages for multiple queries.
No login required — uses Indeed's public listing pages.
"""
import os
import re
import time
import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate

def _first(selectors):
    """Get first element from Scrapling Selectors, or None."""
    try:
        return selectors.first if selectors and len(selectors) > 0 else None
    except Exception:
        return None

SEARCH_QUERIES = [
    # ── Montreal Intern Queries ──
    ("intern", "Montreal, QC", "ca.indeed.com"),
    ("stage", "Montreal, QC", "ca.indeed.com"),
    ("stagiaire", "Montreal, QC", "ca.indeed.com"),
    ("co-op", "Montreal, QC", "ca.indeed.com"),
    ("summer intern", "Montreal, QC", "ca.indeed.com"),
    ("software intern", "Montreal, QC", "ca.indeed.com"),
    ("software engineering intern", "Montreal, QC", "ca.indeed.com"),
    ("data intern", "Montreal, QC", "ca.indeed.com"),
    ("stagiaire informatique", "Montreal, QC", "ca.indeed.com"),
    ("frontend intern", "Montreal, QC", "ca.indeed.com"),
    ("backend intern", "Montreal, QC", "ca.indeed.com"),

    # ── Toronto Intern Queries ──
    ("software intern", "Toronto, ON", "ca.indeed.com"),
    ("intern", "Toronto, ON", "ca.indeed.com"),
    ("co-op", "Toronto, ON", "ca.indeed.com"),
    ("data intern", "Toronto, ON", "ca.indeed.com"),

    # ── Vancouver Intern Queries ──
    ("software intern", "Vancouver, BC", "ca.indeed.com"),
    ("intern", "Vancouver, BC", "ca.indeed.com"),
    ("co-op", "Vancouver, BC", "ca.indeed.com"),

    # ── Ottawa Intern Queries ──
    ("software intern", "Ottawa, ON", "ca.indeed.com"),
    ("intern", "Ottawa, ON", "ca.indeed.com"),
    ("co-op", "Ottawa, ON", "ca.indeed.com"),

    # ── Canada-wide & Remote Intern Queries ──
    ("software intern", "Canada", "ca.indeed.com"),
    ("intern", "Canada", "ca.indeed.com"),
    ("co-op", "Canada", "ca.indeed.com"),
    ("internship", "Canada", "ca.indeed.com"),
    ("student", "Canada", "ca.indeed.com"),

    # ── Other Major Cities Intern Queries ──
    ("software intern", "Calgary, AB", "ca.indeed.com"),
    ("software intern", "Edmonton, AB", "ca.indeed.com"),
    ("software intern", "Winnipeg, MB", "ca.indeed.com"),
    ("software intern", "Halifax, NS", "ca.indeed.com"),
    ("software intern", "Quebec City, QC", "ca.indeed.com"),
    ("software intern", "Kitchener, ON", "ca.indeed.com"),
    ("software intern", "Waterloo, ON", "ca.indeed.com"),


]

INDEED_FROM_AGE = int(os.getenv("INDEED_FROM_AGE", "30"))
INDEED_QUERY_DELAY = float(os.getenv("INDEED_QUERY_DELAY", "0.5"))
INDEED_BETWEEN_QUERY_DELAY = float(os.getenv("INDEED_BETWEEN_QUERY_DELAY", "0.25"))
INDEED_SKILL_LIMIT = int(os.getenv("INDEED_SKILL_LIMIT", "8"))
INDEED_BLOCK_LIMIT = int(os.getenv("INDEED_BLOCK_LIMIT", "5"))

def scrape_indeed_jobs(dynamic_skills: List[str] = None) -> List[JobCreate]:
    """Scrape Indeed public job listings using Scrapling's StealthyFetcher."""
    queries = list(SEARCH_QUERIES)
    if dynamic_skills:
        for skill in dynamic_skills[:INDEED_SKILL_LIMIT]:
            queries.insert(0, (f"{skill} intern", "Canada", "ca.indeed.com"))
            queries.insert(0, (f"{skill} developer", "Montreal, QC", "ca.indeed.com"))
            queries.insert(0, (f"{skill} engineer", "Canada", "ca.indeed.com"))
    try:
        from scrapling.fetchers import StealthyFetcher
    except ImportError:
        print("[Indeed] scrapling not installed.")
        return []

    jobs: List[JobCreate] = []
    seen_urls = set()
    blocked_count = 0

    for keywords, location, domain in queries:
        # Indeed blocks pagination after page 1 (redirects to login).
        # We only scrape page 1 per query but use many queries to compensate.
        for start_idx in [0]:
            try:
                # Add delay to avoid immediate blocking from heavy pagination
                if start_idx > 0:
                    time.sleep(INDEED_QUERY_DELAY)
                q = keywords.replace(' ', '+')
                l = location.replace(' ', '+').replace(',', '%2C')
                url = f"https://{domain}/jobs?q={q}&l={l}&sort=date&fromage={INDEED_FROM_AGE}&start={start_idx}"
                print(f"  [Indeed] Searching: '{keywords}' in '{location}' (start={start_idx})...")

                page = StealthyFetcher.fetch(url, headless=True, network_idle=True)

                if page.status != 200:
                    print(f"  [Indeed] Got status {page.status}")
                    if page.status in (403, 429):
                        blocked_count += 1
                        if blocked_count >= INDEED_BLOCK_LIMIT:
                            print("  [Indeed] Too many blocks, stopping early.")
                            return jobs
                    continue
                blocked_count = 0

                # Try multiple card selectors
                job_cards = page.css('div.job_seen_beacon')
                if not job_cards or len(job_cards) == 0:
                    job_cards = page.css('.cardOutline')
                if not job_cards or len(job_cards) == 0:
                    job_cards = page.css('.result')
                if not job_cards or len(job_cards) == 0:
                    job_cards = page.css('[data-jk]')

                print(f"  [Indeed] Found {len(job_cards)} cards")
                if len(job_cards) == 0:
                    break

                for card in job_cards:
                    try:
                        # Title
                        title_el = _first(card.css('h2.jobTitle span[title]')) or _first(card.css('h2.jobTitle a')) or _first(card.css('h2 a')) or _first(card.css('.jobTitle'))
                        if title_el:
                            title = title_el.attrib.get('title', '') or title_el.text
                            title = title.strip()
                        else:
                            continue

                        # Company
                        company_el = _first(card.css('[data-testid="company-name"]')) or _first(card.css('span.companyName')) or _first(card.css('.company'))
                        company = company_el.text.strip() if company_el else "Unknown"

                        # Location
                        loc_el = _first(card.css('[data-testid="text-location"]')) or _first(card.css('div.companyLocation')) or _first(card.css('.location'))
                        loc = loc_el.text.strip() if loc_el else location

                        # URL
                        jk_el = _first(card.css('[data-jk]'))
                        job_key = jk_el.attrib.get('data-jk', '') if jk_el else card.attrib.get('data-jk', '')
                        link_el = _first(card.css('a[id]')) or _first(card.css('h2 a'))

                        if job_key:
                            job_url = f"https://{domain}/viewjob?jk={job_key}"
                        elif link_el:
                            href = link_el.attrib.get('href', '')
                            job_url = f"https://{domain}{href}" if href.startswith('/') else href
                        else:
                            continue

                        # Clean URL if it's not a viewjob link
                        if '?' in job_url and not job_url.startswith(f"https://{domain}/viewjob"):
                            if 'jk=' in job_url:
                                import re
                                match = re.search(r'jk=([a-zA-Z0-9]+)', job_url)
                                if match:
                                    job_url = f"https://{domain}/viewjob?jk={match.group(1)}"
                                else:
                                    job_url = job_url.split('?')[0]
                            else:
                                job_url = job_url.split('?')[0]

                        if not title or not job_url or job_url in seen_urls:
                            continue
                        seen_urls.add(job_url)

                        # Remote
                        combined = f"{title} {loc}".lower()
                        remote = "remote" in combined or "télétravail" in combined

                        # Salary snippet (if present)
                        salary_el = _first(card.css('.salary-snippet-container')) or _first(card.css('.salaryOnly')) or _first(card.css('.metadata.salary-snippet-container'))
                        salary = salary_el.text.strip() if salary_el else None

                        # Job type
                        title_lower = title.lower()
                        job_type = "Full-time"
                        if any(kw in title_lower for kw in ["intern", "stage", "stagiaire", "internship"]):
                            job_type = "Internship"
                        elif any(kw in title_lower for kw in ["junior", "jr", "new grad", "entry level", "graduate"]):
                            job_type = "New Grad"
                        elif "contract" in title_lower or "freelance" in title_lower:
                            job_type = "Contract"

                        # Description snippet
                        desc_ul = card.css('ul')
                        if desc_ul and len(desc_ul) > 0:
                            description = desc_ul[0].text.strip()
                        else:
                            desc_el = _first(card.css('.job-snippet'))
                            description = desc_el.text.strip() if desc_el else f"{title} at {company}"

                        # Check metadata for additional tags
                        for meta in card.css('[class*="metadata"]'):
                            mt = meta.text.lower()
                            if "internship" in mt or "stage" in mt:
                                job_type = "Internship"
                            elif "contract" in mt:
                                job_type = "Contract"

                        jobs.append(JobCreate(
                            title=title[:250],
                            company=company[:250],
                            location=loc[:250] if loc else None,
                            remote=remote,
                            description=description[:5000],
                            url=job_url,
                            source="Indeed",
                            salary=salary,
                            job_type=job_type,
                        ))
                    except Exception:
                        continue
                        
                time.sleep(INDEED_QUERY_DELAY)
            except Exception as e:
                print(f"  [Indeed] Error during scraping '{keywords}': {e}")
                
            time.sleep(INDEED_BETWEEN_QUERY_DELAY)

    return jobs

if __name__ == "__main__":
    jobs = scrape_indeed_jobs(["react"])
    print(f"Found {len(jobs)} jobs")
    if jobs:
        print(jobs[0].dict())
