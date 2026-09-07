import sys
import dagshub
import mlflow

from src.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain
)
from src.logger import logging
from src.exception import multi_agent

# Initialize DagsHub tracking for the project
dagshub.init(repo_owner='abdallahatefhatem', repo_name='LangChain-Multi-Agent-Research-System', mlflow=True)

def run_research_pipeline(topic: str) -> dict:
    """
    Executes a multi-agent research pipeline:
    1. Search Agent -> Fetches initial web sources.
    2. Reader Agent -> Scrapes top relevant URLs for context.
    3. Writer Chain -> Drafts a structured research report.
    4. Critic Chain -> Reviews and evaluates the report.
    """
    state = {}

    try:
        logging.info(f"Starting multi-agent research pipeline for topic: '{topic}'")

        # ── Step 1: Search Agent ──────────────────────────────────────────
        logging.info("Step 1/4: Executing Search Agent...")
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable, and detailed information about: {topic}")]
        })

        state["search_results"] = search_result['messages'][-1].content
        logging.info("Search Agent completed successfully.")

        # ── Step 2: Reader Agent ──────────────────────────────────────────
        logging.info("Step 2/4: Executing Reader Agent (Scraping)...")
        reader_agent = build_reader_agent()
        
        # Pass full or soft-limited search context to prevent missing top URLs
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URLs and scrape them for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:2000]}"
            )]
        })

        state['scraped_content'] = reader_result['messages'][-1].content
        logging.info("Reader Agent completed scraping.")

        # ── Step 3: Writer Chain ─────────────────────────────────────────
        logging.info("Step 3/4: Executing Writer Chain...")
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )

        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })
        logging.info("Writer Chain completed drafting report.")

        # ── Step 4: Critic Chain ─────────────────────────────────────────
        logging.info("Step 4/4: Executing Critic Chain...")
        state["feedback"] = critic_chain.invoke({
            "report": state['report']
        })
        logging.info("Critic Chain completed report review.")

        logging.info("Research pipeline finished successfully.")
        
        # ── Log Results to MLflow (DagsHub) ───────────────────────────────
        with mlflow.start_run(run_name=f"Research_{topic.replace(' ', '_')[:20]}"):
            mlflow.log_param("topic", topic)
            mlflow.log_metric("report_length", len(state.get("report", "")))
            mlflow.log_metric("search_results_length", len(state.get("search_results", "")))
            mlflow.log_text(state.get("report", ""), "final_report.txt")
            mlflow.log_text(state.get("feedback", ""), "critic_feedback.txt")

        return state

    except Exception as e:
        logging.error("An error occurred during pipeline execution.")
        raise multi_agent(e, sys)


if __name__ == "__main__":
    # Test execution
    result = run_research_pipeline("who is messi?")
    print("\n" + "=" * 50)
    print("FINAL REPORT:\n", result.get("report"))
    print("\n" + "=" * 50)
    print("CRITIC FEEDBACK:\n", result.get("feedback"))