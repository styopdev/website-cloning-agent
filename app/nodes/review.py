import json

from langchain_ollama import ChatOllama
from pathlib import Path


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0,
    num_predict=256,
    format="json",
    client_kwargs={"timeout": 300.0},
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT_ROOT / "workspace"


def parse_review_response(content):
    try:
        result = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "The language model returned an invalid structured website review."
        ) from error

    if (
        not isinstance(result, dict)
        or not isinstance(result.get("approved"), bool)
        or not isinstance(result.get("feedback"), str)
    ):
        raise RuntimeError(
            "The language model returned an incomplete structured website review."
        )

    feedback = result["feedback"].strip()
    if not result["approved"] and not feedback:
        raise RuntimeError(
            "The language model rejected the website without providing feedback."
        )

    return result["approved"], feedback


def review_website(state):
    print("Reviewing the generated site with the local model...", flush=True)
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    files = {}

    for filename in ["index.html", "style.css", "script.js"]:

        file_path = WORKSPACE / filename

        if file_path.exists():
            files[filename] = file_path.read_text(
                encoding="utf-8"
            )

    prompt = f"""
    You are a senior frontend developer.

    Review this generated website against the user's request and website
    analysis. Evaluate the requested features rather than assuming a specific
    business domain.

    User request:
    {state["user_request"]}

    Website analysis:
    {state["website_analysis"]}

    Browser test results:
    {state.get("browser_test_results", "")}

    {files}

    Check:
    1. HTML structure
    2. CSS problems
    3. JavaScript errors
    4. Whether requested user flows and features work
    5. Responsive design and accessibility
    6. Missing requirements or broken links between the three files

    Verify each issue against the supplied source before reporting it. Do not
    claim that an element, tag, or selector is missing unless you checked the
    corresponding file. Browser errors are authoritative when present.

    Return only a JSON object with boolean key "approved" and string key
    "feedback". When approved, feedback must be "APPROVED". Otherwise provide
    at most three short, actionable corrections, each naming the relevant
    file or browser error. Do not include an issue that is not supported by
    the supplied source.
    """

    response_parts = []
    chunk_count = 0
    print("Review in progress", end="", flush=True)
    for chunk in llm.stream(prompt):
        if isinstance(chunk.content, str):
            response_parts.append(chunk.content)
            chunk_count += 1
            if chunk_count % 50 == 0:
                print(".", end="", flush=True)

    if chunk_count >= 50:
        print()
    response_text = "".join(response_parts).strip()
    if not response_text:
        raise RuntimeError("The language model returned an empty website review.")

    approved, feedback = parse_review_response(response_text)
    if approved:
        feedback = "APPROVED"

    print(
        "Review approved." if approved else "Review found changes to make.",
        flush=True,
    )
    return {
        "review_feedback": feedback,
        "approved": approved
    }