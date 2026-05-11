from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:3000/login")
    page.fill('input[type="email"]', "subagent_testing@example.com")
    page.fill('input[type="password"]', "agentSecure123!")
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/dashboard")
    page.goto("http://localhost:3000/resume")
    page.set_input_files('input[type="file"]', "C:/Users/olimi/OneDrive - ETS/jobfinder/test_resume.pdf")
    
    with page.expect_response("http://127.0.0.1:8001/api/v1/resume/upload") as response_info:
        page.click('button[type="submit"]')
    
    response = response_info.value
    print(f"Status: {response.status}")
    print(f"Body: {response.text()}")
    browser.close()
