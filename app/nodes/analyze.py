from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)


def analyze_website(state):

    research_data = state["research_data"]

    prompt = f"""
    You are an expert website designer and frontend architect.

    Analyze this website research data:

    {research_data}

    Identify:

    1. Website purpose
    2. Main layout and structure
    3. Navigation
    4. Important sections
    5. Design characteristics
    6. Functional features
    7. Suggested implementation plan

    Provide a structured analysis.
    """

    response = llm.invoke(prompt)

    return {
        "website_analysis": response.content
    }