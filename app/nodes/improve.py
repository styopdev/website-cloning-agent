from pathlib import Path
from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)


def improve_website(state):

    workspace = Path("workspace")

    feedback = state["review_feedback"]

    for filename in ["index.html", "style.css", "script.js"]:

        file_path = workspace / filename

        if not file_path.exists():
            continue

        original_code = file_path.read_text(encoding="utf-8")

        prompt = f"""
        You are a senior frontend developer.

        Fix the following website file.

        Review feedback:
        {feedback}

        Current file: {filename}

        Current code:
        {original_code}

        Return ONLY the complete corrected file content.
        Do not use markdown code fences.
        """

        response = llm.invoke(prompt)

        file_path.write_text(
            response.content.strip(),
            encoding="utf-8"
        )

    return {
        "revision_count": state["revision_count"] + 1
    }