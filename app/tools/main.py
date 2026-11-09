from app.tools.graph import build_graph


def main():

    agent = build_graph()

    print("\n=== Website Cloning Agent ===\n")

    user_request = input("What website do you want to build? ")
    website_url = input(
        "Reference website URL (optional; leave blank to search): "
    ).strip()

    initial_state = {
        "user_request": user_request,
        "website_url": website_url,
        "research_data": "",
        "website_analysis": "",
        "generated_files": [],
        "review_feedback": "",
        "approved": False,
        "revision_count": 0,
        "browser_test_results": ""
    }

    print("\nAgent started...\n")

    result = agent.invoke(initial_state)

    print("\n=== Agent Results ===")
    print(f"\nReference website: {result['website_url']}")

    print("\nGenerated files:")

    for file in result["generated_files"]:
        print(f"- {file}")

    print("\nReview feedback:")
    print(result["review_feedback"])


if __name__ == "__main__":
    main()