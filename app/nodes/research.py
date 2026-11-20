from base64 import urlsafe_b64decode
import json
import re
from urllib.parse import parse_qs, quote, urlsplit

from langchain_ollama import ChatOllama
from playwright.sync_api import Error as PlaywrightError, sync_playwright


candidate_llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0,
    format="json",
    num_predict=384,
    client_kwargs={"timeout": 300.0},
)

SEARCH_STOP_WORDS = {
    "about",
    "best",
    "build",
    "create",
    "design",
    "for",
    "from",
    "good",
    "make",
    "modern",
    "online",
    "page",
    "responsive",
    "shop",
    "site",
    "store",
    "style",
    "the",
    "website",
    "with",
}


def _validate_url(url):
    if not urlsplit(url).scheme:
        url = f"https://{url}"

    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Expected an absolute http(s) URL, got: {url!r}")
    return url


def _parse_suggested_candidates(content):
    try:
        result = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "The local model returned invalid candidate-search data."
        ) from error

    if not isinstance(result, dict) or not isinstance(result.get("candidates"), list):
        raise RuntimeError(
            "The local model returned no candidate list for reference search."
        )

    urls = []
    for candidate in result["candidates"]:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("url"), str):
            continue
        try:
            url = _validate_url(candidate["url"].strip())
        except ValueError:
            continue
        if url not in urls:
            urls.append(url)
    return urls


def _unwrap_bing_result(href):
    parsed = urlsplit(href)
    if parsed.hostname not in {"bing.com", "www.bing.com"}:
        return href

    encoded_url = parse_qs(parsed.query).get("u", [""])[0]
    if not encoded_url.startswith("a1"):
        return href

    encoded_url = encoded_url[2:]
    encoded_url += "=" * (-len(encoded_url) % 4)
    try:
        return urlsafe_b64decode(encoded_url).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return href


def _candidate_score(user_request, result_text, candidate_url):
    query_words = {
        word
        for word in re.findall(r"[a-z0-9]+", user_request.lower())
        if len(word) > 2 and word not in SEARCH_STOP_WORDS
    }
    if not query_words:
        return 0

    candidate_words = set(
        re.findall(r"[a-z0-9]+", f"{result_text} {candidate_url}".lower())
    )
    return sum(
        word in candidate_words
        or (word.endswith("s") and word[:-1] in candidate_words)
        or (word + "s" in candidate_words)
        for word in query_words
    )


def _minimum_candidate_score(user_request):
    terms = {
        word
        for word in re.findall(r"[a-z0-9]+", user_request.lower())
        if len(word) > 2 and word not in SEARCH_STOP_WORDS
    }
    return max(1, (len(terms) + 1) // 2)


def _find_reference(page, user_request):
    query = quote(f"{user_request} website")
    searches = (
        (
            "Bing",
            f"https://www.bing.com/search?q={query}",
            "li.b_algo h2 a",
        ),
        (
            "DuckDuckGo",
            f"https://html.duckduckgo.com/html/?q={query}",
            "a.result__a",
        ),
    )
    errors = []

    for engine, search_url, result_selector in searches:
        print(f"Searching {engine} for a reference...", flush=True)
        try:
            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=30000,
            )
        except PlaywrightError as error:
            errors.append(f"{engine}: {error}")
            continue

        candidates = []
        for rank, result in enumerate(page.locator(result_selector).all()):
            href = result.get_attribute("href")
            if not href:
                continue

            candidate = _unwrap_bing_result(href)
            parsed = urlsplit(candidate)
            hostname = (parsed.hostname or "").lower()
            if (
                parsed.scheme in {"http", "https"}
                and parsed.netloc
                and hostname not in {"bing.com", "www.bing.com", "duckduckgo.com"}
                and not hostname.endswith(".duckduckgo.com")
            ):
                result_text = result.evaluate(
                    """element => {
                        const card = element.closest("li.b_algo, .result");
                        return card ? card.textContent : element.textContent;
                    }"""
                )
                score = _candidate_score(
                    user_request,
                    result_text or "",
                    candidate,
                )
                if score >= _minimum_candidate_score(user_request):
                    candidates.append((score, -rank, candidate))

        if candidates:
            candidate = max(candidates)[2]
            print(f"Selected reference candidate: {candidate}", flush=True)
            return candidate

    print(
        "Search engines returned no relevant results. Asking the local model "
        "for known candidates to verify...",
        flush=True,
    )
    prompt = f"""
Suggest up to three real, established websites that best match this category:
{user_request}

Prefer official businesses with a public homepage suitable as a visual
reference. Do not invent domains. Return only JSON in this shape:
{{"candidates":[{{"url":"https://example.com","reason":"brief fit"}}]}}
"""
    print("Finding known candidates with the local model...", flush=True)
    response_parts = []
    chunk_count = 0
    for chunk in candidate_llm.stream(prompt):
        if isinstance(chunk.content, str):
            response_parts.append(chunk.content)
            chunk_count += 1
            if chunk_count % 50 == 0:
                print(".", end="", flush=True)
    if chunk_count >= 50:
        print()
    suggested_urls = _parse_suggested_candidates("".join(response_parts))

    verified_candidates = []
    for rank, candidate_url in enumerate(suggested_urls):
        print(f"Verifying candidate {candidate_url}...", flush=True)
        candidate_page = page.context.new_page()
        try:
            response = candidate_page.goto(
                candidate_url,
                wait_until="domcontentloaded",
                timeout=20000,
            )
            if not response or response.status >= 400:
                continue
            title = candidate_page.title()
            body_text = candidate_page.locator("body").inner_text(timeout=5000)[:1200]
        except PlaywrightError:
            continue
        finally:
            candidate_page.close()

        score = _candidate_score(
            user_request,
            f"{title} {body_text}",
            candidate_url,
        )
        if score >= _minimum_candidate_score(user_request):
            verified_candidates.append((score, -rank, candidate_url))

    if verified_candidates:
        candidate = max(verified_candidates)[2]
        print(f"Selected verified reference candidate: {candidate}", flush=True)
        return candidate

    details = " ".join(errors)
    raise RuntimeError(
        "Could not verify a suitable reference website. No generic site was "
        "created. Try a more specific description or provide a reference URL."
        + (f" Search errors: {details}" if details else "")
    )


def research_website(state):
    url = state.get("website_url", "").strip()
    user_request = state.get("user_request", "").strip()

    if not user_request:
        raise ValueError("A website description is required to search for a reference.")

    if url:
        url = _validate_url(url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context()
            page = context.new_page()
            if not url:
                url = _find_reference(page, user_request)

            print(f"Researching reference website {url}...", flush=True)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except PlaywrightError as error:
                raise RuntimeError(
                    f"Could not open reference website {url}: {error}"
                ) from error

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