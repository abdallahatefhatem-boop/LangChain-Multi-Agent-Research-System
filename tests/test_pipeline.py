import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.pipeline import pipeline


class TestResearchPipeline(unittest.TestCase):
    @patch.object(pipeline, "critic_chain")
    @patch.object(pipeline, "writer_chain")
    @patch.object(pipeline, "build_reader_agent")
    @patch.object(pipeline, "build_search_agent")
    def test_runs_all_four_pipeline_stages(
        self,
        build_search_agent,
        build_reader_agent,
        writer_chain,
        critic_chain,
    ):
        search_agent = MagicMock()
        search_agent.invoke.return_value = {
            "messages": [
                SimpleNamespace(content="Title: Example\nURL: https://example.com")
            ]
        }
        reader_agent = MagicMock()
        reader_agent.invoke.return_value = {
            "messages": [SimpleNamespace(content="Useful source content")]
        }
        build_search_agent.return_value = search_agent
        build_reader_agent.return_value = reader_agent
        writer_chain.invoke.return_value = "A research report"
        critic_chain.invoke.return_value = "Score: 9/10"

        result = pipeline.run_research_pipeline("Renewable energy")

        self.assertEqual(result["search_results"], "Title: Example\nURL: https://example.com")
        self.assertEqual(result["scraped_content"], "Useful source content")
        self.assertEqual(result["report"], "A research report")
        self.assertEqual(result["feedback"], "Score: 9/10")
        search_agent.invoke.assert_called_once()
        reader_agent.invoke.assert_called_once()
        writer_chain.invoke.assert_called_once()
        critic_chain.invoke.assert_called_once()

    @patch.object(pipeline, "build_reader_agent")
    @patch.object(pipeline, "build_search_agent")
    def test_reader_receives_at_most_2000_search_characters(
        self,
        build_search_agent,
        build_reader_agent,
    ):
        search_agent = MagicMock()
        search_agent.invoke.return_value = {
            "messages": [SimpleNamespace(content="x" * 3000)]
        }
        reader_agent = MagicMock()
        reader_agent.invoke.return_value = {
            "messages": [SimpleNamespace(content="source content")]
        }
        build_search_agent.return_value = search_agent
        build_reader_agent.return_value = reader_agent

        with patch.object(pipeline, "writer_chain") as writer_chain, patch.object(
            pipeline, "critic_chain"
        ) as critic_chain:
            writer_chain.invoke.return_value = "report"
            critic_chain.invoke.return_value = "feedback"
            pipeline.run_research_pipeline("Test topic")

        reader_prompt = reader_agent.invoke.call_args.args[0]["messages"][0][1]
        self.assertEqual(len(reader_prompt.split("Search Results:\n", 1)[1]), 2000)


if __name__ == "__main__":
    unittest.main()
