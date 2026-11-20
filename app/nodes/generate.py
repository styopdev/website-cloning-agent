from langchain_ollama import ChatOllama
from pathlib import Path
import json
import re


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0,
    format="json",
    client_kwargs={"timeout": 300.0},
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT_ROOT / "workspace"
EXPECTED_FILES = {"index.html", "style.css", "script.js"}


def parse_generated_files(output):
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, dict):
        return {
            filename: content.strip()
            for filename, content in payload.items()
            if filename in EXPECTED_FILES
            and isinstance(content, str)
            and content.strip()
        }

    pattern = (
        r"(?im)^FILE:\s*([A-Za-z0-9_.-]+)\s*$"
        r"\s*```(?:[A-Za-z0-9_-]+)?\s*\n?"
        r"(.*?)"
        r"\n?```"
    )
    matches = re.findall(pattern, output, re.DOTALL)
    files = {}
    for filename, content in matches:
        filename = filename.strip()
        if filename in EXPECTED_FILES:
            files[filename] = content.strip()
    return files


def generate_website(state):

    analysis = state["website_analysis"]
    user_request = state.get("user_request", "")

    prompt = f"""
    You are an expert frontend developer.

    Recreate the reference website's visible layout, page hierarchy, styling,
    and interactions as closely as practical, using the analysis as the source
    of truth. Apply any additional user requirements:

    User request:
    {user_request}

    Website analysis:
    {analysis}

    Requirements:
    - HTML5
    - CSS3
    - Vanilla JavaScript
    - Responsive design
    - Accessible, semantic markup and usable keyboard interactions
    - Deliver a polished, visually rich result, not a bare HTML page with
      default browser styling
    - Translate the reference's measured palette, typography, spacing, nav,
      section widths, and component geometry into concrete CSS
    - Give the header, hero, content sections, product cards, controls, and
      footer distinct, intentional layout and spacing
    - Keep all visual presentation in style.css; do not set inline styles from
      JavaScript
    - Implement the visible features and interactions observed on the reference
    - Use original branding, copy, and assets; do not reproduce the reference
      site's logo, proprietary text, source code, or distinctive brand identity
    - Do not reference image files or URLs that were not provided; use CSS
      artwork or inline SVG elements where visual assets are needed. Do not
      use data-URI img placeholders.
    - Do not invent backend integrations; make demo interactions work locally

    Return only a valid JSON object with exactly these three string keys:
    "index.html", "style.css", and "script.js". Each value must contain the
    complete source code for that file. Do not use Markdown fences or include
    explanations.
    """

    print(
        "Generating the website files with the local model. "
        "This step can take a few minutes...",
        flush=True,
    )
    response = llm.invoke(prompt)

    output = response.content

    WORKSPACE.mkdir(parents=True, exist_ok=True)

    generated_files = []
    parsed_files = parse_generated_files(output)
    missing = sorted(
        filename
        for filename in EXPECTED_FILES
        if not parsed_files.get(filename, "").strip()
    )
    if missing:
        raise RuntimeError(
            "The language model did not return all required website files: "
            + ", ".join(missing)
        )

    print("Writing generated website files...", flush=True)
    for filename in ["index.html", "style.css", "script.js"]:
        file_path = WORKSPACE / filename

        file_path.write_text(
            parsed_files[filename],
            encoding="utf-8"
        )

        generated_files.append(str(file_path))

    print("Website files generated.", flush=True)
    return {
        "generated_files": generated_files
    }