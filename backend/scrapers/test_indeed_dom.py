from scrapling.fetchers import StealthyFetcher
import time

url = "https://ca.indeed.com/jobs?q=react+developer&l=Montreal%2C+QC&fromage=7&sort=date&start=0"
page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
print(f"Status: {page.status}")

with open("indeed_dom.html", "w", encoding="utf-8") as f:
    f.write(page.text)

cards = page.css('div.job_seen_beacon')
print(f"div.job_seen_beacon: {len(cards)}")

cards2 = page.css('td.resultContent')
print(f"td.resultContent: {len(cards2)}")

cards3 = page.css('div.slider_container')
print(f"div.slider_container: {len(cards3)}")

cards4 = page.css('li.css-5lfssm')
print(f"li.css-5lfssm: {len(cards4)}")
