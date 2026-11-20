import unittest
import json
from types import SimpleNamespace
from unittest.mock import patch

from app.nodes.analyze import analyze_website
from app.nodes.generate import parse_generated_files
from app.nodes.improve import clean_model_file
from app.nodes.research import research_website
from app.nodes.review import parse_review_response, review_website
from app.tools.graph import review_router


class NodeHelperTests(unittest.TestCase):
    def test_analysis_combines_streamed_model_output(self):
        with patch("app.nodes.analyze.llm") as model:
            model.stream.return_value = [
                SimpleNamespace(content="Concise "),
                SimpleNamespace(content="analysis"),
            ]
            result = analyze_website({
                "user_request": "A bakery homepage",
                "research_data": "{}",
            })

        self.assertEqual(result["website_analysis"], "Concise analysis")

    def test_review_combines_streamed_approval(self):
        with patch("app.nodes.review.llm") as model:
            model.stream.return_value = [
                SimpleNamespace(
                    content=json.dumps({
                        "approved": True,
                        "feedback": "APPROVED",
                    })
                ),
            ]
            result = review_website({
                "user_request": "A bakery homepage",
                "website_analysis": "A concise storefront",
                "browser_test_results": "{}",
            })

        self.assertEqual(result["review_feedback"], "APPROVED")
        self.assertTrue(result["approved"])

    def test_parse_review_response_requires_concise_json_fields(self):
        response = json.dumps({
            "approved": False,
            "feedback": "Fix the missing local image in style.css.",
        })
        approved, feedback = parse_review_response(response)
        self.assertFalse(approved)
        self.assertEqual(feedback, "Fix the missing local image in style.css.")

    def test_parse_generated_files_accepts_fenced_response(self):
        output = """
FILE: index.html
```html
<main>Hello</main>
```
FILE: style.css
```css
main { color: green; }
```
FILE: script.js
```javascript
console.log("ready");
```
"""
        files = parse_generated_files(output)
        self.assertEqual(set(files), {"index.html", "style.css", "script.js"})
        self.assertEqual(files["index.html"], "<main>Hello</main>")

    def test_parse_generated_files_accepts_json_response(self):
        expected = {
            "index.html": "<main>Hello</main>",
            "style.css": "main { color: green; }",
            "script.js": 'console.log("ready");',
        }
        files = parse_generated_files(json.dumps(expected))
        self.assertEqual(files, expected)

    def test_parse_generated_files_rejects_missing_file(self):
        files = parse_generated_files("FILE: index.html\n```html\n<h1>Hi</h1>\n```")
        self.assertEqual(set(files), {"index.html"})

    def test_clean_model_file_removes_fences(self):
        self.assertEqual(
            clean_model_file("```html\n<main>Hi</main>\n```"),
            "<main>Hi</main>",
        )

    def test_review_router_uses_state_without_assumptions(self):
        self.assertEqual(review_router({}), "improve")
        self.assertEqual(review_router({"approved": True}), "end")
        self.assertEqual(
            review_router({"approved": False, "revision_count": 1}),
            "end",
        )

    def test_research_requires_a_reference_url(self):
        with self.assertRaisesRegex(ValueError, "reference website URL is required"):
            research_website({
                "website_url": "",
                "user_request": "A bakery homepage",
            })


if __name__ == "__main__":
    unittest.main()
