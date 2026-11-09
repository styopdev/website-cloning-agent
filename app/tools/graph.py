from langgraph.graph import StateGraph, START, END
from app.nodes.browser_test import browser_test
from app.tools.state import AgentState
from app.nodes.research import research_website
from app.nodes.analyze import analyze_website
from app.nodes.generate import generate_website
from app.nodes.review import review_website
from app.nodes.improve import improve_website


def review_router(state):

    if state["approved"]:
        return "end"

    if state["revision_count"] >= 2:
        return "end"

    return "improve"


def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("research", research_website)
    graph.add_node("analyze", analyze_website)
    graph.add_node("generate", generate_website)
    graph.add_node("browser_test", browser_test)
    graph.add_node("review", review_website)
    graph.add_node("improve", improve_website)

    graph.add_edge(START, "research")
    graph.add_edge("research", "analyze")
    graph.add_edge("analyze", "generate")
    graph.add_edge("generate", "browser_test")
    graph.add_edge("browser_test", "review")

    graph.add_conditional_edges(
        "review",
        review_router,
        {
            "improve": "improve",
            "end": END
        }
    )

    graph.add_edge("improve", "browser_test")

    return graph.compile()