import json
from pathlib import Path

from playwright.sync_api import sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT_ROOT / "workspace"


def browser_test(state):
    print("Checking the generated site in Chromium...", flush=True)
    website = WORKSPACE / "index.html"
    screenshot = WORKSPACE / "screenshot.png"

    if not website.is_file():
        raise FileNotFoundError(
            f"Generated website not found: {website}"
        )

    WORKSPACE.mkdir(parents=True, exist_ok=True)
    errors = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "console",
                lambda message: (
                    errors.append(message.text)
                    if message.type == "error"
                    else None
                ),
            )

            page.goto(
                website.resolve().as_uri(),
                wait_until="domcontentloaded",
                timeout=60000,
            )
            title = page.title()
            headings = page.locator("h1").all_text_contents()
            page.screenshot(path=str(screenshot), full_page=True)
        finally:
            browser.close()

    results = {
        "title": title,
        "headings": headings,
        "javascript_errors": errors,
        "has_title": bool(title),
        "has_heading": bool(headings),
    }

    print("Browser check complete.", flush=True)
    return {
        "browser_test_results": json.dumps(results, ensure_ascii=False)
    }