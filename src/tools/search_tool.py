from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from rich import print
import getpass
import os
from src.logger import logging
from src.exception import multi_agent
import sys
from ensure import ensure_annotations
from langchain.tools import tool



try:
    logging.info("get tavily api key....")

    if not os.environ.get("TAVILY_API_KEY"):

        # os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")
        load_dotenv()
    logging.info("used tavily api key ")

except Exception as e:

    logging.debug("there is not tavikly api key")
    raise multi_agent(e,sys)


try:
    tool_ = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
    )
    @tool
    @ensure_annotations
    
    def query(text: str):

        """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
        logging.info("getting response....")

        response=tool_.invoke({"query": text})

        logging.info("reuturn response")
        out = []


        for r in response['results']:

            out.append(
                f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
            )

        logging.info("appended title url content")

        return "\n----\n".join(out)
        # print( "\n----\n".join(out))

except Exception as e:
    logging.debug("there is error in response ")

    raise multi_agent(e ,sys)

# query("what is AI?")
