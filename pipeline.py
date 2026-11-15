
from collections.abc import Callable

from agents import build_scrape_agent, build_search_agent, writer_chain, critic_chain


def run_research_pipeline(
    topic: str,
    on_progress: Callable[[str], None] | None = None,
) -> dict:

    state = {}

    def report_progress(message: str) -> None:
        if on_progress is not None:
            on_progress(message)

    # STEP 1 - SEARCH AGENT
    report_progress("Searching the web for reliable sources...")
    print("\n" + " =" * 50)
    print("STEP 1 - SEARCH AGENT IS CONDUCTING RESEARCH ...")
    print("=" * 50)

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [
            (
                "user",
                f"Find 3 reliable sources about {topic}. Return each title, URL, "
                "and one-sentence summary. Keep under 120 words; do not invent."
            )
        ]
    })

    state["search_results"] = search_result["messages"][-1].content[:2500]

    print("\nSearch Results:\n", state["search_results"])


    # STEP 2 - READER AGENT
    report_progress("Reading the most relevant source...")
    print("\n" + " =" * 50)
    print("STEP 2 - READER AGENT IS EXTRACTING DEEPER INSIGHTS ...")
    print("=" * 50)

    reader_agent = build_scrape_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            (
                "user",
                f"Topic: {topic}\nFind the best source in these results, scrape it, "
                f"and return its URL plus up to 100 words of verified facts:\n"
                f"{state['search_results']}"
            )
        ]
    })

    state["scraped_content"] = reader_result["messages"][-1].content[:2500]

    print("\nScraped Content:\n", state["scraped_content"])


    # STEP 3 - WRITER AGENT
    report_progress("Writing your concise research report...")
    print("\n" + " =" * 50)
    print("STEP 3 - WRITER AGENT IS PREPARING THE RESEARCH REPORT ...")
    print("=" * 50)

    research_combined = (
        f"INITIAL WEB RESEARCH:\n{state['search_results']}\n\n"
        f"DETAILED SOURCE ANALYSIS:\n{state['scraped_content']}"
    )[:5000]

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    if not state["report"].strip():
        raise RuntimeError(
            "The writer returned an empty report. Wait for the Groq rate limit to reset and retry."
        )

    print("\nFINAL RESEARCH REPORT:\n", state["report"])


    # STEP 4 - CRITIC AGENT
    report_progress("Reviewing the report for clarity and evidence...")
    print("\n" + " =" * 50)
    print("STEP 4 - CRITIC AGENT IS PERFORMING QUALITY EVALUATION ...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\nCRITICAL REVIEW AND EVALUATION:\n", state["feedback"])


    return state


if __name__ == "__main__":

    topic = input("\nEnter a research topic: ")

    run_research_pipeline(topic)
