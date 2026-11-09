from playwright.sync_api import sync_playwright


def research_website(state):
    url = state["website_url"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        title = page.title()
        description = page.locator(
            'meta[name="description"]'
        ).get_attribute("content") or ""

        headings = page.locator("h1, h2, h3").all_text_contents()
        links = page.locator("a").all_text_contents()

        research_data = {
            "url": url,
            "title": title,
            "description": description,
            "headings": headings,
            "links": links[:50],
        }

        browser.close()

    return {"research_data": str(research_data)}