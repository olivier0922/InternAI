"""
Job Scraper Runner v3.0
Aggregates jobs from all sources (APIs + web scrapers) and inserts into Supabase.
Handles deduplication by URL.
"""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

load_dotenv(Path(__file__).parent.parent / ".env")

from scrapers.hn_scraper import scrape_hn_jobs
from scrapers.remotive_scraper import scrape_remotive_jobs
from scrapers.arbeitnow_scraper import scrape_arbeitnow_jobs
from scrapers.findwork_scraper import scrape_findwork_jobs
from scrapers.jobicy_scraper import scrape_jobicy_jobs
from scrapers.themuse_scraper import scrape_themuse_jobs
from scrapers.himalayas_scraper import scrape_himalayas_jobs
from scrapers.linkedin_scraper import scrape_linkedin_jobs
from scrapers.indeed_scraper import scrape_indeed_jobs
from scrapers.glassdoor_scraper import scrape_glassdoor_jobs
from scrapers.weworkremotely_scraper import scrape_weworkremotely_jobs
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

supabase: Client = None
if url and key:
    supabase = create_client(url, key)

_has_new_columns = None

def check_new_columns():
    global _has_new_columns
    if _has_new_columns is not None:
        return _has_new_columns
    try:
        supabase.table("jobs").select("job_type").limit(1).execute()
        _has_new_columns = True
    except Exception:
        _has_new_columns = False
    return _has_new_columns


from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def clean_url(url: str) -> str:
    """Remove common tracking parameters to prevent duplicates."""
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        # Remove common tracking params
        for param in ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'ref', 'source', 'campaign', 'jrtk', 'pos', 'ao', 's', 'guid']:
            qs.pop(param, None)
        new_query = urlencode(qs, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    except:
        return url

def is_canada(location: str) -> bool:
    """Return True if location appears to be in Canada, or is Remote/unspecified."""
    if not location:
        return True  # Unknown location — keep it
    loc = location.lower().strip()

    # Always keep remote / flexible / worldwide
    if any(kw in loc for kw in ["remote", "anywhere", "worldwide", "global", "flexible", "work from home", "wfh"]):
        return True

    # Canadian indicators
    ca_provinces = [
        "canada", "montreal", "montréal", "toronto", "vancouver", "ottawa",
        "calgary", "edmonton", "winnipeg", "quebec", "québec", "halifax",
        "kitchener", "waterloo", "victoria", "saskatoon", "regina",
        "hamilton", "london, on", "brampton", "mississauga", "laval",
        "gatineau", "markham", "burnaby", "surrey", "richmond, bc",
        ", qc", ", on", ", bc", ", ab", ", mb", ", sk", ", ns", ", nb",
        ", pe", ", nl", "ontario", "british columbia", "alberta",
        "manitoba", "saskatchewan", "nova scotia", "new brunswick",
    ]
    if any(kw in loc for kw in ca_provinces):
        return True

    return False


def insert_jobs(jobs, source_name):
    if not supabase:
        print(f"  [WARN] Supabase not configured. Would have inserted {len(jobs)} jobs.")
        return 0

    inserted = 0
    batch_data = []
    
    has_cols = check_new_columns()

    # Track seen URLs in this batch to prevent intra-batch dupes
    seen_urls = set()
    skipped_location = 0

    for job in jobs:
        # Filter: only Internships
        if job.job_type != "Internship":
            continue

        # Filter: only Canada jobs
        if not is_canada(job.location):
            skipped_location += 1
            continue

        if not job.url:
            continue
        cleaned_url = clean_url(job.url)
        if cleaned_url in seen_urls:
            continue
        seen_urls.add(cleaned_url)
        
        row = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "remote": job.remote,
            "description": job.description,
            "salary": job.salary,
            "url": cleaned_url,
            "source": job.source
        }
        
        if has_cols:
            row["job_type"] = job.job_type
            row["tags"] = job.tags

        batch_data.append(row)

    if skipped_location > 0:
        print(f"  [FILTER] Skipped {skipped_location} non-Canada jobs")

    if not batch_data:
        return 0

    try:
        res = supabase.table("jobs").upsert(batch_data, on_conflict="url").execute()
        inserted = len(res.data)
    except Exception as e:
        print(f"  [ERROR] Database insert failed for {source_name}: {e}")

    return inserted


def run_scraper_safe(name, func):
    start = time.time()
    try:
        jobs = func()
        elapsed = time.time() - start
        return name, jobs, elapsed, None
    except Exception as e:
        elapsed = time.time() - start
        return name, [], elapsed, str(e)


def run_scraper_group(scrapers, max_workers: int):
    if max_workers <= 1 or len(scrapers) <= 1:
        return [run_scraper_safe(name, func) for name, func in scrapers]

    order = {name: i for i, (name, _) in enumerate(scrapers)}
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_scraper_safe, name, func): name
            for name, func in scrapers
        }
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                name = futures[future]
                results.append((name, [], 0.0, str(e)))

    results.sort(key=lambda r: order.get(r[0], 0))
    return results


def get_user_skills():
    if not supabase: return []
    skills_set = set()
    try:
        res = supabase.table("resumes").select("extracted_skills").execute()
        for row in res.data:
            if row.get("extracted_skills"):
                for s in row["extracted_skills"]:
                    skills_set.add(s)
    except Exception as e:
        print(f"  [WARN] Failed to fetch user skills: {e}")
    return list(skills_set)


def sanitize_keywords(keywords):
    allowed_digit = ["c++", "c#", "node.js", "next.js", "vue3", "react18", "html5", "css3"]
    broad_terms = [
        "software", "developer", "engineer", "intern", "internship", "co-op",
        "new grad", "junior", "entry", "frontend", "backend", "full stack",
        "python", "javascript", "typescript", "java", "c++", "c#", "node",
        "react", "angular", "vue", "sql", "data", "ml", "ai", "devops",
        "cloud", "security", "qa", "test", "mobile", "ios", "android",
    ]
    cleaned = []
    seen = set()
    for kw in keywords:
        k = (kw or "").strip()
        if len(k) < 3 or len(k) > 32:
            continue
        if not any(ch.isalpha() for ch in k):
            continue
        lower = k.lower()
        if not any(term in lower for term in broad_terms):
            continue
        if any(ch.isdigit() for ch in k):
            if not any(p in lower for p in allowed_digit):
                continue
        if lower in seen:
            continue
        seen.add(lower)
        cleaned.append(k)
    return cleaned

from rss_scrapers import scrape_remoteok_jobs, scrape_nodesk_jobs

def run_scrapers():
    """Main entry point — NOT async to avoid Playwright Sync API conflicts."""
    print("=" * 60)
    print("  InternAI Job Scraper Pipeline v3.0")
    print("  Sources: 11 (8 APIs + 3 Web Scrapers)")
    print("=" * 60)

    if not supabase:
        print("\nERROR: SUPABASE_URL or SUPABASE_KEY not found.")
        return
        
    dynamic_skills = get_user_skills()

    # Force broad search terms to ensure lots of intern/entry roles in Canada
    base_keywords = [
        "intern", "internship", "co-op", "student", "new grad",
        "junior", "entry level", "software intern", "developer intern",
        "data intern", "qa intern", "montreal intern", "canada intern",
    ]
    dynamic_skills = list(dict.fromkeys(dynamic_skills + base_keywords))
    dynamic_skills = sanitize_keywords(dynamic_skills)
    dynamic_skill_limit = int(os.getenv("SCRAPER_SKILL_LIMIT", "12"))
    dynamic_skills = dynamic_skills[:dynamic_skill_limit]

    max_api_workers = int(os.getenv("SCRAPER_API_WORKERS", "6"))
    max_web_workers = int(os.getenv("SCRAPER_WEB_WORKERS", "2"))

    if dynamic_skills:
        print(f"  Using {len(dynamic_skills)} keywords to target: {', '.join(dynamic_skills[:5])}...")

    api_scrapers = [
        ("WeWorkRemotely", scrape_weworkremotely_jobs),
        ("RemoteOK", scrape_remoteok_jobs),
        ("NoDesk", scrape_nodesk_jobs),
        ("Remotive", scrape_remotive_jobs),
        ("Arbeitnow", scrape_arbeitnow_jobs),
        ("FindWork", scrape_findwork_jobs),
        ("Hacker News", scrape_hn_jobs),
        ("Jobicy", scrape_jobicy_jobs),
        ("The Muse", scrape_themuse_jobs),
        ("Himalayas", scrape_himalayas_jobs),
    ]

    web_scrapers = [
        ("LinkedIn", lambda: scrape_linkedin_jobs(dynamic_skills)),
        ("Indeed", lambda: scrape_indeed_jobs(dynamic_skills)),
        ("Glassdoor", lambda: scrape_glassdoor_jobs(dynamic_skills)),
    ]

    total_found = 0
    total_inserted = 0
    all_scrapers = api_scrapers + web_scrapers

    print(f"\n--- Phase 1: API Scrapers ({len(api_scrapers)} sources) ---")
    print(f"  API workers: {max_api_workers}")
    api_results = run_scraper_group(api_scrapers, max_api_workers)
    for i, (name, jobs, elapsed, error) in enumerate(api_results, 1):
        print(f"\n[{i}/{len(all_scrapers)}] Fetching from {name}...")
        if error:
            print(f"  [SKIP] {name} failed ({elapsed:.1f}s): {error}")
            continue
        print(f"  Found {len(jobs)} jobs ({elapsed:.1f}s)")
        count = insert_jobs(jobs, name)
        print(f"  Inserted {count} new jobs")
        total_found += len(jobs)
        total_inserted += count

    print(f"\n--- Phase 2: Web Scrapers ({len(web_scrapers)} sources) ---")
    print("  (These use Scrapling StealthyFetcher — takes longer)")
    print(f"  Web workers: {max_web_workers}")
    web_results = run_scraper_group(web_scrapers, max_web_workers)
    for i, (name, jobs, elapsed, error) in enumerate(web_results, len(api_scrapers) + 1):
        print(f"\n[{i}/{len(all_scrapers)}] Scraping {name}...")
        if error:
            print(f"  [SKIP] {name} failed ({elapsed:.1f}s): {error}")
            continue
        print(f"  Found {len(jobs)} jobs ({elapsed:.1f}s)")
        count = insert_jobs(jobs, name)
        print(f"  Inserted {count} new jobs")
        total_found += len(jobs)
        total_inserted += count

    print("\n" + "=" * 60)
    print(f"  DONE: Found {total_found} total | Inserted {total_inserted} new jobs")
    print("=" * 60)


if __name__ == "__main__":
    run_scrapers()
