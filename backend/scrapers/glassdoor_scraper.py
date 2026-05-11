"""
Glassdoor Jobs Scraper (via Scrapling StealthyFetcher)
Scrapes Glassdoor's public job search pages.
"""
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
    ("software engineer", "Montreal"),
    ("developer", "Montreal"),
    ("software intern", "Montreal"),
    ("devops", "Montreal"),
    ("software engineer", "Toronto"),
    ("python developer", "Toronto"),
    ("software engineer", "Canada"),
    ("full stack developer", "Canada"),
    ("react developer", ""),
    ("machine learning engineer", ""),
]


def scrape_glassdoor_jobs(dynamic_skills: List[str] = None) -> List[JobCreate]:
    """Scrape Glassdoor public job listings using Scrapling's StealthyFetcher."""
    queries = list(SEARCH_QUERIES)
    if dynamic_skills:
        for skill in dynamic_skills[:10]:
            queries.insert(0, (f"{skill} developer", "Montreal"))
            queries.insert(0, (f"{skill} engineer", "Toronto"))
    try:
        from scrapling.fetchers import StealthyFetcher
    except ImportError:
        print("[Glassdoor] scrapling not installed.")
        return []

    jobs: List[JobCreate] = []
    seen_urls = set()

    for keywords, location in queries:
        for page_num in range(1, 6):
            try:
                if page_num > 1:
                    time.sleep(3.5)
                kw = keywords.replace(' ', '-')
                loc_param = f"&locKeyword={location.replace(' ', '+')}" if location else ""
                ip_param = f"_IP{page_num}" if page_num > 1 else ""
                url = f"https://www.glassdoor.com/Job/{kw}-jobs-SRCH_KO0,{len(kw)}{ip_param}.htm?fromAge=7{loc_param}"
                print(f"  [Glassdoor] Searching: '{keywords}' in '{location}' (page {page_num})...")

                page = StealthyFetcher.fetch(url, headless=True, network_idle=True)

                if page.status != 200:
                    print(f"  [Glassdoor] Got status {page.status}")
                    continue

                # Glassdoor cards: data-test="jobListing"
                job_cards = page.css('[data-test="jobListing"]')
                if not job_cards or len(job_cards) == 0:
                    job_cards = page.css('li.JobsList_jobListItem__wjTHv')
                if not job_cards or len(job_cards) == 0:
                    job_cards = page.css('.react-job-listing')

                print(f"  [Glassdoor] Found {len(job_cards)} cards")

                for card in job_cards:
                    try:
                        # Title — a.JobCard_jobTitle__GLyJ1 with data-test="job-title"
                        title_el = _first(card.css('[data-test="job-title"]')) or _first(card.css('a.JobCard_jobTitle__GLyJ1'))
                        title = title_el.text.strip() if title_el else None

                        # Company
                        company_el = (
                            _first(card.css('span[class*="EmployerProfile_compactEmployerName"]')) or
                            _first(card.css('[class*="compactEmployerName"]')) or
                            _first(card.css('[class*="employerName"]')) or
                            _first(card.css('.EmployerProfile_employerNameContainer__ptolz span'))
                        )
                        if company_el:
                            company = company_el.text.strip()
                        else:
                            company = "Unknown"
                        # Fallback: check img alt attribute for company logo
                        if company == "Unknown":
                            img_el = _first(card.css('img[alt]'))
                            if img_el:
                                alt = img_el.attrib.get('alt', '')
                                if alt and 'logo' in alt.lower():
                                    company = alt.replace(' Logo', '').replace(' logo', '').strip()

                        # Location — [data-test="emp-location"] or class*="location"
                        loc_el = (
                            _first(card.css('[data-test="emp-location"]')) or
                            _first(card.css('[class*="JobCard_location"]')) or
                            _first(card.css('[class*="location"]'))
                        )
                        loc = loc_el.text.strip() if loc_el else location

                        # URL
                        link_el = title_el if title_el and title_el.tag == 'a' else _first(card.css('a[href*="/job-listing/"]'))
                        href = link_el.attrib.get('href', '') if link_el else ''
                        if href and not href.startswith('http'):
                            job_url = f"https://www.glassdoor.com{href}"
                        else:
                            job_url = href

                        if not title or not job_url or job_url in seen_urls:
                            continue
                        seen_urls.add(job_url)

                        # Salary
                        salary_el = (
                            _first(card.css('[data-test="detailSalary"]')) or
                            _first(card.css('[class*="JobCard_salaryEstimate"]')) or
                            _first(card.css('[class*="salary-estimate"]'))
                        )
                        salary = salary_el.text.strip() if salary_el else None

                        # Description
                        desc = f"{title} at {company}"
                        if loc:
                            desc += f" in {loc}"

                        # Remote
                        combined = f"{title} {loc}".lower()
                        remote = "remote" in combined

                        # Job type
                        title_lower = title.lower()
                        job_type = "Full-time"
                        if any(kw in title_lower for kw in ["intern", "stage", "stagiaire", "internship"]):
                            job_type = "Internship"
                        elif any(kw in title_lower for kw in ["junior", "jr", "new grad", "entry"]):
                            job_type = "New Grad"
                        elif "contract" in title_lower:
                            job_type = "Contract"

                        jobs.append(JobCreate(
                            title=title[:250],
                            company=company[:250],
                            location=loc[:250] if loc else None,
                            remote=remote,
                            description=desc[:5000],
                            url=job_url,
                            source="Glassdoor",
                            salary=salary,
                            job_type=job_type,
                        ))
                    except Exception:
                        continue

                time.sleep(3)
            except Exception as e:
                print(f"  [Glassdoor] Error for '{keywords}' in '{location}': {e}")
                time.sleep(3)

    return jobs


if __name__ == "__main__":
    results = scrape_glassdoor_jobs()
    print(f"\nFound {len(results)} total jobs from Glassdoor")
    for j in results[:15]:
        print(f"  - {j.title} @ {j.company} [{j.location}] ({j.job_type}) {j.salary or ''}")
