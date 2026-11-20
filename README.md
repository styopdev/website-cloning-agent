# Website Cloning Agent

This project uses a local Ollama model and Playwright to recreate a website's
layout and visible interactions from a reference URL it finds or one you provide.

## Run the agent

Use one of these commands from the project directory:

```powershell
.\venv\Scripts\python.exe -m app.tools.main
```

Or open **Run and Debug** in VS Code and choose **Website Cloning Agent**.
The prompts appear in the integrated terminal.

Describe the kind of website you want to clone. You can optionally provide a
reference URL; otherwise, the agent searches Bing and DuckDuckGo, then asks the
local model to suggest and verify candidates if search results are blocked.
It stops instead of generating a generic site if no candidate can be verified.
For example:

```text
An online shop for trail-running shoes with product categories and a cart
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
