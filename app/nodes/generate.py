from langchain_ollama import ChatOllama
from pathlib import Path


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)


def generate_website(state):

    analysis = state["website_analysis"]

    prompt = f"""
    You are an expert frontend developer.

    Build an original pizza delivery website based on this analysis:

    {analysis}

    Requirements:
    - HTML5
    - CSS3
    - Vanilla JavaScript
    - Responsive design
    - Modern user interface
    - Pizza menu with prices
    - Shopping cart
    - Add to cart functionality

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