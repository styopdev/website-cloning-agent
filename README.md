# Website Cloning Agent

This project uses a local Ollama model and Playwright to recreate a website's
layout and visible interactions from a required reference URL.

## Run the agent

Use one of these commands from the project directory:

```powershell
.\venv\Scripts\python.exe -m app.tools.main
```

Or open **Run and Debug** in VS Code and choose **Website Cloning Agent**.
The prompts appear in the integrated terminal.

Enter the URL of the website you want to recreate. A reference URL is required;
the agent will stop instead of generating a generic site if one is missing.
Then enter optional instructions or press Enter to match the reference layout.
For example:

```text
https://example.com
```

The result uses original branding, copy, and assets rather than copying a
third-party site's logo or proprietary content.

Ollama must be running locally with the required model:

```powershell
ollama run llama3.1:8b
```

## Preview generated files

Start the preview only after the agent has generated the files:

```powershell
.\venv\Scripts\python.exe -m http.server 8000 --directory workspace
```

Open `http://localhost:8000`.

## Run tests

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```
