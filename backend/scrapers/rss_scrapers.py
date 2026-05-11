import feedparser
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from schemas.job import JobCreate
import urllib.request
from bs4 import BeautifulSoup
import re

def scrape_rss_feed(feed_url, source_name, headers=None):
    jobs = []
    print(f"Fetching {source_name} RSS...")
    try:
        req = urllib.request.Request(feed_url, headers=headers or {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            feed_data = response.read()
        
        parsed = feedparser.parse(feed_data)
        print(f"  [{source_name}] Found {len(parsed.entries)} jobs")
        
        for entry in parsed.entries:
            title = entry.get('title', 'Unknown Title')
            link = entry.get('link', '')
            desc_html = entry.get('description', '')
            
            # Try to extract company from title "Company: Title" or similar
            company = "Unknown"
            if " at " in title:
                parts = title.split(" at ")
                title = parts[0].strip()
                company = parts[1].strip()
            elif " - " in title:
                parts = title.split(" - ")
                company = parts[0].strip()
                title = " - ".join(parts[1:]).strip()
            elif " | " in title:
                parts = title.split(" | ")
                title = parts[0].strip()
                company = parts[1].strip()
                
            # clean desc
            soup = BeautifulSoup(desc_html, "html.parser")
            desc = soup.get_text(separator=" ", strip=True)
            
            if not desc:
                desc = title
                
            jobs.append(JobCreate(
                title=title,
                company=company,
                location="Remote",
                remote=True,
                description=desc,
                salary=None,
                url=link,
                source=source_name,
                job_type="All",
                tags=[]
            ))
            
    except Exception as e:
        print(f"  [ERROR] {source_name} scraper failed: {e}")
        
    return jobs

def scrape_remoteok_jobs(*args):
    return scrape_rss_feed("https://remoteok.com/rss", "RemoteOK")

def scrape_nodesk_jobs(*args):
    return scrape_rss_feed("https://nodesk.co/remote-jobs/rss.xml", "NoDesk")
