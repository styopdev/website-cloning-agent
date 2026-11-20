import json
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def _validate_url(url):
    if not urlsplit(url).scheme:
        url = f"https://{url}"

    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Expected an absolute http(s) URL, got: {url!r}")
    return url


def research_website(state):
    url = state.get("website_url", "").strip()

    if not url:
        raise ValueError(
            "A reference website URL is required; no generic site was created."
        )

    url = _validate_url(url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            print(f"Researching reference website {url}...", flush=True)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            title = page.title()
            description_meta = page.locator('meta[name="description"]')
            description = (
                description_meta.get_attribute("content")
                if description_meta.count()
                else ""
            )

            headings = page.locator("h1, h2, h3").all_text_contents()
            links = page.locator("a").all_text_contents()
            buttons = page.locator(
                "button, [role='button']"
            ).all_text_contents()
            page_text = page.locator("body").inner_text()[:4000]
            visual_profile = page.locator("body").evaluate(
                """body => Array.from(
                    body.querySelectorAll(
                        "header, nav, main, section, article, footer, "
                        + "h1, h2, button, a"
                    )
                ).filter(element => {
                    const rect = element.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                }).slice(0, 18).map(element => {
                    const style = getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    return {
                        tag: element.tagName.toLowerCase(),
                        className: String(element.className || "").slice(0, 80),
                        text: (element.innerText || "").replace(/\\s+/g, " ").trim().slice(0, 80),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        display: style.display,
                        background: style.backgroundColor,
                        color: style.color,
                        font: style.font,
                        padding: style.padding,
                        margin: style.margin,
                        gap: style.gap
                    };
                })"""
            )

            research_data = {
                "url": url,
                "title": title,
                "description": description or "",
                "headings": headings[:30],
                "links": links[:20],
                "buttons": buttons[:20],
                "page_text": page_text,
                "visual_profile": visual_profile,
            }

        finally:
            browser.close()

    return {
        "website_url": url,
        "research_data": json.dumps(research_data, ensure_ascii=False),
    }