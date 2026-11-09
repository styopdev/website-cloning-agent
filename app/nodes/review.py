from langchain_ollama import ChatOllama
from pathlib import Path


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)


def review_website(state):

    workspace = Path("workspace")

    files = {}

    for filename in ["index.html", "style.css", "script.js"]:

        file_path = workspace / filename

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

    {files}

    Check:
    1. HTML structure
    2. CSS problems
    3. JavaScript errors
    4. Whether requested user flows and features work
    5. Responsive design and accessibility
    6. Missing requirements or broken links between the three files

    Explain what needs fixing.

    If everything is acceptable, include the exact word APPROVED on its own
    line. Otherwise, do not use that word as a standalone line.
    """

    response = llm.invoke(prompt)

    feedback = response.content

    approved = any(
        line.strip().upper() == "APPROVED"
        for line in feedback.splitlines()
    )

    return {
        "review_feedback": feedback,
        "approved": approved
    }