"""Debug Glassdoor card structure"""
from scrapling.fetchers import StealthyFetcher

def _first(selectors):
    try:
        return selectors.first if selectors and len(selectors) > 0 else None
    except Exception:
        return None

url = "https://www.glassdoor.com/Job/software-engineer-jobs-SRCH_KO0,17.htm?fromAge=7&locKeyword=Montreal"
print(f"Fetching Glassdoor...")

page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
print(f"Status: {page.status}")
print(f"Actual URL: {page.url}")

# Try various card selectors
for sel in ['[data-test="jobListing"]', '.react-job-listing', '.jobCard', 'li[data-id]', 'li.JobsList_jobListItem__wjTHv']:
    cards = page.css(sel)
    if cards and len(cards) > 0:
        print(f"\nFound {len(cards)} cards with: {sel}")
        card = cards[0]
        print(f"Card HTML saved to card_html.txt")
        with open("card_html.txt", "w", encoding="utf-8") as f:
            f.write(card.html_content)
            
        company_el = (
            card.css('span[class*="EmployerProfile_compactEmployerName"]') or
            card.css('[class*="compactEmployerName"]') or
            card.css('[class*="employerName"]') or
            card.css('.EmployerProfile_employerNameContainer__ptolz span')
        )
        if company_el:
            company_el = company_el[0]
            print(f"Company element found: {company_el.html_content}")
            print(f"Company text: '{company_el.text}'")
        else:
            print("Company element NOT found")
        break
else:
    print("No cards found with known selectors")
    # Show page structure
    all_li = page.css('li')
    print(f"Total li elements: {len(all_li)}")
    all_a = page.css('a[href*="/job-listing/"]')
    print(f"Job listing links: {len(all_a)}")
    for a in all_a[:3]:
        print(f"  Link: {a.text.strip()[:80]} -> {a.attrib.get('href','')[:80]}")
