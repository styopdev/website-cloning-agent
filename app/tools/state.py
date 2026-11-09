from typing import TypedDict


class AgentState(TypedDict):
    user_request: str
    website_url: str
    research_data: str
    website_analysis: str
    generated_files: list[str]
    review_feedback: str
    approved: bool
    revision_count: int
    browser_test_results: str