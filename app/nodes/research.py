import json
from urllib.parse import quote, urljoin, urlsplit

from playwright.sync_api import sync_playwright


def _validate_url(url):
    if not urlsplit(url).scheme:
        url = f"https://{url}"

    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Expected an absolute http(s) URL, got: {url!r}")
    return url


def _find_reference(page, user_request):
    search_url = (
        "https://html.duckduckgo.com/html/?q="
        + quote(user_request, safe="")
    )
    page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

    for result in page.locator("a.result__a").all():
        href = result.get_attribute("href")
        if not href:
            continue

        candidate = urljoin(search_url, href)
        parsed = urlsplit(candidate)
        hostname = (parsed.hostname or "").lower()
        if (
            parsed.scheme in {"http", "https"}
            and parsed.netloc
            and hostname != "duckduckgo.com"
            and not hostname.endswith(".duckduckgo.com")
        ):
            return candidate

    raise RuntimeError(
        "Web search did not return a usable reference site. "
        "Try again or provide a reference URL."
    )


def research_website(state):
    url = state.get("website_url", "").strip()
    user_request = state.get("user_request", "").strip()

    if not url and not user_request:
        raise ValueError("Provide a website request or a reference URL.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            if not url:
                url = _find_reference(page, user_request)

            url = _validate_url(url)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            title = page.title()
            description = page.locator(
                'meta[name="description"]'
            ).get_attribute("content") or ""

            headings = page.locator("h1, h2, h3").all_text_contents()
            links = page.locator("a").all_text_contents()
            buttons = page.locator(
                "button, [role='button']"
            ).all_text_contents()
            page_text = page.locator("body").inner_text()[:10000]

            research_data = {
                "url": url,
                "title": title,
                "description": description,
                "headings": headings[:60],
                "links": links[:60],
                "buttons": buttons[:30],
                "page_text": page_text,
            }

        finally:
            browser.close()

    return {
        "website_url": url,
        "research_data": json.dumps(research_data, ensure_ascii=False),
    }