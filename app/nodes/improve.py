from pathlib import Path
from langchain_ollama import ChatOllama
from app.nodes.generate import EXPECTED_FILES, parse_generated_files


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0,
    format="json",
    client_kwargs={"timeout": 300.0},
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT_ROOT / "workspace"


def clean_model_file(response):
    content = response.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else ""
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]
    return content.strip()


def improve_website(state):

    WORKSPACE.mkdir(parents=True, exist_ok=True)

    feedback = state["review_feedback"]
    print("Applying review feedback in one model call...", flush=True)
    files = {}

    for filename in ["index.html", "style.css", "script.js"]:
        file_path = WORKSPACE / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Generated website file not found: {file_path}")
        files[filename] = file_path.read_text(encoding="utf-8")

    prompt = f"""
You are a senior frontend developer. Apply the review feedback to this website.
Keep working features and styling that do not need changes.

Review feedback:
{feedback}

Current website files:
{files}

Return only a valid JSON object with exactly these string keys:
"index.html", "style.css", and "script.js". Each value must contain the full
corrected source for that file. Do not include Markdown fences or explanations.
"""
    response = llm.invoke(prompt)
    updated_files = parse_generated_files(response.content)
    missing = sorted(
        filename
        for filename in EXPECTED_FILES
        if not updated_files.get(filename, "").strip()
    )
    if missing:
        raise RuntimeError(
            "The language model did not return all corrected website files: "
            + ", ".join(missing)
        )

    for filename in ["index.html", "style.css", "script.js"]:
        (WORKSPACE / filename).write_text(
            clean_model_file(updated_files[filename]),
            encoding="utf-8",
        )

    return {
        "revision_count": state.get("revision_count", 0) + 1
    }