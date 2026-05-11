import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from run import insert_jobs
from indeed_scraper import scrape_indeed_jobs
from glassdoor_scraper import scrape_glassdoor_jobs

def run_fast():
    print("Running Fast Indeed + Glassdoor...")
    
    # 1. Indeed
    print("\n--- INDEED ---")
    jobs = scrape_indeed_jobs(["react", "python"])
    print(f"Indeed found {len(jobs)} jobs")
    inserted = insert_jobs(jobs, "Indeed")
    print(f"Inserted {inserted} Indeed jobs")
    
    # 2. Glassdoor
    print("\n--- GLASSDOOR ---")
    jobs = scrape_glassdoor_jobs(["react", "python"])
    print(f"Glassdoor found {len(jobs)} jobs")
    inserted = insert_jobs(jobs, "Glassdoor")
    print(f"Inserted {inserted} Glassdoor jobs")

if __name__ == "__main__":
    run_fast()
