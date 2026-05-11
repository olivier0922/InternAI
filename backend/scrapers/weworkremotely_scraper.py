import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate

def scrape_weworkremotely_jobs() -> list[JobCreate]:
    """Scrape WeWorkRemotely RSS feed."""
    url = "https://weworkremotely.com/remote-jobs.rss"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching WeWorkRemotely RSS: {e}")
        return []

    jobs = []
    try:
        root = ET.fromstring(response.content)
        for item in root.findall('./channel/item'):
            title_node = item.find('title')
            link_node = item.find('link')
            desc_node = item.find('description')
            cat_node = item.find('category')
            
            if title_node is None or link_node is None:
                continue
                
            raw_title = title_node.text or ""
            link = link_node.text or ""
            raw_desc = desc_node.text if desc_node is not None else ""
            category = cat_node.text if cat_node is not None else ""
            
            # WWR format is typically "Company: Job Title"
            company = "Unknown"
            title = raw_title
            if ":" in raw_title:
                parts = raw_title.split(":", 1)
                company = parts[0].strip()
                title = parts[1].strip()
                
            # Clean description
            soup = BeautifulSoup(raw_desc, "html.parser")
            description = soup.get_text(separator=" ").strip()
            
            # Categories as tags
            tags = []
            if category:
                tags.append(category)
                
            job_type = "Full-time"
            if "intern" in title.lower() or "intern" in category.lower():
                job_type = "Internship"
            elif "contract" in title.lower() or "contract" in category.lower():
                job_type = "Contract"

            jobs.append(JobCreate(
                title=title,
                company=company,
                location="Remote",
                remote=True,
                description=description,
                url=link,
                source="WeWorkRemotely",
                job_type=job_type,
                tags=tags,
                salary=None
            ))
    except Exception as e:
        print(f"Error parsing WeWorkRemotely RSS: {e}")
        
    return jobs

if __name__ == "__main__":
    jobs = scrape_weworkremotely_jobs()
    print(f"Found {len(jobs)} jobs from WeWorkRemotely.")
    if jobs:
        print(jobs[0].dict())
