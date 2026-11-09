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

    Review this generated website.

    {files}

    Check:
    1. HTML structure
    2. CSS problems
    3. JavaScript errors
    4. Shopping cart functionality
    5. Responsive design
    6. Missing features

    Explain what needs fixing.

    If everything is acceptable, respond with APPROVED.
    """

    response = llm.invoke(prompt)

    feedback = response.content

    approved = "APPROVED" in feedback.upper()

    return {
        "review_feedback": feedback,
        "approved": approved
    }