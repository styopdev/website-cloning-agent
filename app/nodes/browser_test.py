from pathlib import Path
from playwright.sync_api import sync_playwright


def browser_test(state):

    website = Path("workspace/index.html").resolve()

    errors = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.on("pageerror", lambda error: errors.append(str(error)))

        page.goto(website.as_uri())

        title = page.title()

        headings = page.locator("h1").all_text_contents()

        page.screenshot(
            path="workspace/screenshot.png",
            full_page=True
        )

        browser.close()

    results = {
        "title": title,
        "headings": headings,
        "javascript_errors": errors,
        "has_title": bool(title),
        "has_heading": bool(headings)
    }

    return {
        "browser_test_results": str(results)
    }