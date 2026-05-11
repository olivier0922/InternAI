import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_indeed():
    from indeed_scraper import scrape_indeed_jobs, SEARCH_QUERIES
    print("\nTesting Indeed Scraper...")
    SEARCH_QUERIES.clear()
    SEARCH_QUERIES.append(("react", "Montreal", "ca.indeed.com"))
    jobs = scrape_indeed_jobs()
    print(f"Indeed found {len(jobs)} jobs")
    for j in jobs[:5]:
        print(f" - {j.title} at {j.company} ({j.url})")

if __name__ == "__main__":
    test_indeed()
