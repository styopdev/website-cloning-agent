from app.tools.graph import build_graph


def main():

    agent = build_graph()

    print("\n=== Website Cloning Agent ===\n")

    user_request = input("What kind of website do you want to clone? ").strip()
    if not user_request:
        print("Describe the kind of website you want to clone.")
        return

    website_url = input(
        "Reference URL (optional; leave blank to find the best candidate): "
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