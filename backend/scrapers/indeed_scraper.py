"""
Indeed Jobs Scraper (via Scrapling StealthyFetcher)
Scrapes Indeed's public job search pages for multiple queries.
No login required — uses Indeed's public listing pages.
"""
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
    # ── Montreal General ──
    ("software engineer", "Montreal, QC", "ca.indeed.com"),
    ("developer", "Montreal, QC", "ca.indeed.com"),
    ("data scientist", "Montreal, QC", "ca.indeed.com"),
    ("devops engineer", "Montreal, QC", "ca.indeed.com"),
    ("full stack developer", "Montreal, QC", "ca.indeed.com"),
    ("machine learning", "Montreal, QC", "ca.indeed.com"),
    ("frontend developer", "Montreal, QC", "ca.indeed.com"),
    ("backend developer", "Montreal, QC", "ca.indeed.com"),
    ("python developer", "Montreal, QC", "ca.indeed.com"),
    ("java developer", "Montreal, QC", "ca.indeed.com"),
    ("react developer", "Montreal, QC", "ca.indeed.com"),
    ("cloud engineer", "Montreal, QC", "ca.indeed.com"),
    ("QA engineer", "Montreal, QC", "ca.indeed.com"),
    ("data engineer", "Montreal, QC", "ca.indeed.com"),
    ("security engineer", "Montreal, QC", "ca.indeed.com"),
    ("systems engineer", "Montreal, QC", "ca.indeed.com"),
    ("web developer", "Montreal, QC", "ca.indeed.com"),
    ("mobile developer", "Montreal, QC", "ca.indeed.com"),
    ("AI engineer", "Montreal, QC", "ca.indeed.com"),
    ("site reliability engineer", "Montreal, QC", "ca.indeed.com"),
    ("product manager", "Montreal, QC", "ca.indeed.com"),
    ("UX designer", "Montreal, QC", "ca.indeed.com"),
    ("tech lead", "Montreal, QC", "ca.indeed.com"),

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
    ("développeur", "Montreal, QC", "ca.indeed.com"),
    ("ingénieur logiciel", "Montreal, QC", "ca.indeed.com"),

    # ── Toronto ──
    ("software engineer", "Toronto, ON", "ca.indeed.com"),
    ("developer", "Toronto, ON", "ca.indeed.com"),
    ("python developer", "Toronto, ON", "ca.indeed.com"),
    ("software intern", "Toronto, ON", "ca.indeed.com"),
    ("full stack developer", "Toronto, ON", "ca.indeed.com"),
    ("data scientist", "Toronto, ON", "ca.indeed.com"),
    ("devops", "Toronto, ON", "ca.indeed.com"),
    ("frontend developer", "Toronto, ON", "ca.indeed.com"),
    ("backend developer", "Toronto, ON", "ca.indeed.com"),
    ("java developer", "Toronto, ON", "ca.indeed.com"),
    ("cloud engineer", "Toronto, ON", "ca.indeed.com"),
    ("machine learning", "Toronto, ON", "ca.indeed.com"),
    ("QA engineer", "Toronto, ON", "ca.indeed.com"),
    ("intern", "Toronto, ON", "ca.indeed.com"),
    ("co-op", "Toronto, ON", "ca.indeed.com"),

    # ── Vancouver ──
    ("software engineer", "Vancouver, BC", "ca.indeed.com"),
    ("developer", "Vancouver, BC", "ca.indeed.com"),
    ("software intern", "Vancouver, BC", "ca.indeed.com"),
    ("data scientist", "Vancouver, BC", "ca.indeed.com"),
    ("full stack developer", "Vancouver, BC", "ca.indeed.com"),
    ("devops", "Vancouver, BC", "ca.indeed.com"),

    # ── Ottawa ──
    ("software engineer", "Ottawa, ON", "ca.indeed.com"),
    ("developer", "Ottawa, ON", "ca.indeed.com"),
    ("software intern", "Ottawa, ON", "ca.indeed.com"),
    ("data scientist", "Ottawa, ON", "ca.indeed.com"),

    # ── Canada-wide & Remote ──
    ("react developer", "Canada", "ca.indeed.com"),
    ("backend developer", "Canada", "ca.indeed.com"),
    ("software intern", "Canada", "ca.indeed.com"),
    ("software engineer", "Remote", "ca.indeed.com"),
    ("data engineer", "Canada", "ca.indeed.com"),
    ("full stack developer", "Canada", "ca.indeed.com"),
    ("machine learning", "Canada", "ca.indeed.com"),
    ("devops", "Canada", "ca.indeed.com"),
    ("cloud engineer", "Canada", "ca.indeed.com"),
    ("developer", "Canada", "ca.indeed.com"),
    ("QA", "Canada", "ca.indeed.com"),
    ("security engineer", "Canada", "ca.indeed.com"),
    ("intern", "Canada", "ca.indeed.com"),
    ("co-op", "Canada", "ca.indeed.com"),

    # ── US Major Cities ──
    ("software engineer", "New York, NY", "www.indeed.com"),
    ("developer", "New York, NY", "www.indeed.com"),
    ("software intern", "New York, NY", "www.indeed.com"),
    ("data scientist", "New York, NY", "www.indeed.com"),
    ("software engineer", "San Francisco, CA", "www.indeed.com"),
    ("developer", "San Francisco, CA", "www.indeed.com"),
    ("software intern", "San Francisco, CA", "www.indeed.com"),
    ("software engineer", "Seattle, WA", "www.indeed.com"),
    ("developer", "Seattle, WA", "www.indeed.com"),
    ("software intern", "Seattle, WA", "www.indeed.com"),
    ("software engineer", "Austin, TX", "www.indeed.com"),
    ("developer", "Austin, TX", "www.indeed.com"),
    ("software engineer", "Chicago, IL", "www.indeed.com"),
    ("software engineer", "Boston, MA", "www.indeed.com"),
    ("software engineer", "Los Angeles, CA", "www.indeed.com"),
    ("software engineer", "Denver, CO", "www.indeed.com"),
    ("data scientist", "Remote", "www.indeed.com"),

    # ── US General ──
    ("software engineer", "", "www.indeed.com"),
    ("python developer", "", "www.indeed.com"),
    ("react developer", "Remote", "www.indeed.com"),
    ("full stack developer", "", "www.indeed.com"),
    ("machine learning engineer", "", "www.indeed.com"),
    ("data engineer", "", "www.indeed.com"),
    ("devops engineer", "", "www.indeed.com"),
    ("frontend developer", "Remote", "www.indeed.com"),
    ("backend developer", "Remote", "www.indeed.com"),
    ("software intern", "", "www.indeed.com"),
    ("java developer", "", "www.indeed.com"),
    ("cloud engineer", "", "www.indeed.com"),
    ("security engineer", "", "www.indeed.com"),
    ("QA engineer", "", "www.indeed.com"),
    ("mobile developer", "", "www.indeed.com"),
    ("AI engineer", "", "www.indeed.com"),
]

def scrape_indeed_jobs(dynamic_skills: List[str] = None) -> List[JobCreate]:
    """Scrape Indeed public job listings using Scrapling's StealthyFetcher."""
    queries = list(SEARCH_QUERIES)
    if dynamic_skills:
        for skill in dynamic_skills[:3]:
            queries.insert(0, (f"{skill} developer", "Montreal, QC", "ca.indeed.com"))
            queries.insert(0, (f"{skill} engineer", "Canada", "ca.indeed.com"))
    try:
        from scrapling.fetchers import StealthyFetcher
    except ImportError:
        print("[Indeed] scrapling not installed.")
        return []

    jobs: List[JobCreate] = []
    seen_urls = set()

    for keywords, location, domain in queries:
        # Indeed blocks pagination after page 1 (redirects to login).
        # We only scrape page 1 per query but use many queries to compensate.
        for start_idx in [0]:
            try:
                # Add delay to avoid immediate blocking from heavy pagination
                if start_idx > 0:
                    time.sleep(3)
                q = keywords.replace(' ', '+')
                l = location.replace(' ', '+').replace(',', '%2C')
                url = f"https://{domain}/jobs?q={q}&l={l}&sort=date&start={start_idx}"
                print(f"  [Indeed] Searching: '{keywords}' in '{location}' (start={start_idx})...")

                page = StealthyFetcher.fetch(url, headless=True, network_idle=True)

                if page.status != 200:
                    print(f"  [Indeed] Got status {page.status}")
                    continue

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
                        
                time.sleep(2)
            except Exception as e:
                print(f"  [Indeed] Error during scraping '{keywords}': {e}")
                
        time.sleep(1.5)

    return jobs

if __name__ == "__main__":
    jobs = scrape_indeed_jobs(["react"])
    print(f"Found {len(jobs)} jobs")
    if jobs:
        print(jobs[0].dict())
