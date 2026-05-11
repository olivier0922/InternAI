"""
Job Scraper Runner v3.0
Aggregates jobs from all sources (APIs + web scrapers) and inserts into Supabase.
Handles deduplication by URL.
"""
import os
import sys
import time
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

def is_north_america(location: str) -> bool:
    """Return True if location appears to be in Canada, USA, or is Remote/unspecified."""
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

    # US indicators
    us_states = [
        "united states", "usa", ", us",
        "new york", "san francisco", "los angeles", "chicago", "seattle",
        "austin", "boston", "denver", "dallas", "houston", "atlanta",
        "phoenix", "san diego", "san jose", "portland", "miami",
        "philadelphia", "minneapolis", "detroit", "charlotte",
        "nashville", "raleigh", "pittsburgh", "columbus", "indianapolis",
        "salt lake", "washington", "d.c.", "dc",
        ", ny", ", ca", ", tx", ", wa", ", il", ", ma", ", co", ", ga",
        ", fl", ", pa", ", nc", ", oh", ", mn", ", mi", ", az", ", or",
        ", va", ", md", ", ct", ", nj", ", ut", ", tn", ", mo", ", wi",
        ", in", ", sc", ", ky", ", la", ", ok", ", ia", ", ar", ", ks",
        ", nv", ", nm", ", ne", ", wv", ", id", ", hi", ", me", ", nh",
        ", ri", ", mt", ", de", ", sd", ", nd", ", ak", ", vt", ", wy",
        "california", "texas", "florida", "illinois", "pennsylvania",
        "ohio", "georgia", "north carolina", "michigan", "new jersey",
        "virginia", "massachusetts", "arizona", "colorado", "tennessee",
        "indiana", "maryland", "minnesota", "missouri", "wisconsin",
        "oregon", "connecticut", "iowa", "arkansas", "kansas", "nevada",
        "utah", "kentucky", "louisiana",
    ]
    if any(kw in loc for kw in us_states):
        return True

    # Reject known non-NA countries
    non_na = [
        "germany", "deutschland", "uk", "united kingdom", "london, uk",
        "france", "paris", "india", "bangalore", "mumbai", "delhi",
        "australia", "sydney", "melbourne", "brazil", "são paulo",
        "netherlands", "amsterdam", "spain", "madrid", "barcelona",
        "italy", "milan", "rome", "japan", "tokyo", "china", "beijing",
        "shanghai", "singapore", "ireland", "dublin", "portugal", "lisbon",
        "sweden", "stockholm", "norway", "oslo", "denmark", "copenhagen",
        "finland", "helsinki", "poland", "warsaw", "czech", "prague",
        "austria", "vienna", "switzerland", "zurich", "belgium", "brussels",
        "south korea", "seoul", "taiwan", "israel", "tel aviv",
        "south africa", "nigeria", "kenya", "argentina", "buenos aires",
        "colombia", "bogota", "chile", "santiago", "mexico", "emea",
        "apac", "latam", "europe", "asia", "africa", "middle east",
        "philippines", "manila", "vietnam", "thailand", "bangkok",
        "indonesia", "jakarta", "malaysia", "kuala lumpur", "pakistan",
        "egypt", "cairo", "turkey", "istanbul", "romania", "bucharest",
        "ukraine", "kyiv", "hungary", "budapest", "croatia", "serbia",
        "greece", "athens", "bulgaria", "sofia", "estonia", "tallinn",
        "latvia", "riga", "lithuania", "vilnius", "luxembourg",
    ]
    if any(kw in loc for kw in non_na):
        return False

    # If we can't determine, keep it (benefit of the doubt)
    return True


def insert_jobs(jobs, source_name):
    if not supabase:
        print(f"  [WARN] Supabase not configured. Would have inserted {len(jobs)} jobs.")
        return 0

    inserted = 0
    batch_data = []
    
    has_cols = check_new_columns()

    # Track seen (title, company) in this batch to prevent intra-batch dupes
    seen_batch = set()
    skipped_location = 0

    for job in jobs:
        # Filter: only Canada/USA jobs
        if not is_north_america(job.location):
            skipped_location += 1
            continue

        # Deduplicate by title and company
        sig = (job.title.lower().strip(), job.company.lower().strip())
        if sig in seen_batch:
            continue
        seen_batch.add(sig)

        cleaned_url = clean_url(job.url)
        
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
        print(f"  [FILTER] Skipped {skipped_location} non-Canada/USA jobs")

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
    if dynamic_skills:
        print(f"  Found {len(dynamic_skills)} unique user skills to target: {', '.join(dynamic_skills[:5])}...")

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
    for i, (name, func) in enumerate(api_scrapers, 1):
        print(f"\n[{i}/{len(all_scrapers)}] Fetching from {name}...")
        name, jobs, elapsed, error = run_scraper_safe(name, func)
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
    for i, (name, func) in enumerate(web_scrapers, len(api_scrapers) + 1):
        print(f"\n[{i}/{len(all_scrapers)}] Scraping {name}...")
        name, jobs, elapsed, error = run_scraper_safe(name, func)
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
