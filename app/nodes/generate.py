from langchain_ollama import ChatOllama
from pathlib import Path


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)


def generate_website(state):

    analysis = state["website_analysis"]
    user_request = state.get("user_request", "")

    prompt = f"""
    You are an expert frontend developer.

    Build an original website that fulfills the user's request, using the
    research analysis as design guidance:

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
    - Implement the features and business domain described in the request
    - Use original branding, copy, and assets; do not reproduce the reference
      site's logo, proprietary text, source code, or distinctive brand identity
    - Do not invent backend integrations; make demo interactions work locally

    Return exactly three files:

    FILE: index.html
    ```html
    HTML CODE
    ```

    FILE: style.css
    ```css
    CSS CODE
    ```

    FILE: script.js
    ```javascript
    JAVASCRIPT CODE
    ```

    Do not include explanations.
    """

    response = llm.invoke(prompt)

    output = response.content

    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)

    generated_files = []

    import re

    pattern = r"FILE:\s*(.*?)\s*```(?:\w+)?\s*(.*?)```"

    matches = re.findall(pattern, output, re.DOTALL)
    expected_files = {"index.html", "style.css", "script.js"}
    returned_files = {filename.strip() for filename, _ in matches}
    if len(matches) != len(expected_files) or returned_files != expected_files:
        missing = sorted(expected_files - returned_files)
        raise RuntimeError(
            "The language model did not return all required website files: "
            + ", ".join(missing)
        )

    for filename, content in matches:

        filename = filename.strip()

        if filename not in ["index.html", "style.css", "script.js"]:
            continue

        file_path = workspace / filename

        file_path.write_text(
            content.strip(),
            encoding="utf-8"
        )

        generated_files.append(str(file_path))

    return {
        "generated_files": generated_files
    }