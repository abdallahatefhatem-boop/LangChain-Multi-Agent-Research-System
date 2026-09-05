from langchain_groq import ChatGroq
from src.tools.scrape import scrape_url
from src.tools.search_tool import web_search
from src.logger import logging
from src.exception import multi_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
from dotenv import load_dotenv
from langchain.agents import create_agent
import yaml
import os
from langchain_openrouter import ChatOpenRouter


try:
    logging.info("Loading API key for OpenRouter...")
    load_dotenv()
    
    # Direct OpenRouter integration without ChatOpenAI wrapper
    llm = ChatOpenRouter(
        model="minimax/minimax-m3:free",
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.7,
    )
    logging.info("LLM initialized successfully via ChatOpenRouter.")

except Exception as e:
    logging.error("Error initializing ChatOpenRouter LLM.")
    raise multi_agent(e, sys)

# try:
#     logging.info("lodding api for llm .....")
#     load_dotenv()
#     logging.info("Api key for llm loded")

#     llm=ChatGroq(model="minimax/minimax-m3:free")

# except Exception as e:
#     raise multi_agent(e,sys)
################################################

try:
    logging.info("building search agent ....")

    # 1st Agent : Search Agent
    def build_search_agent():
        return create_agent(
            model= llm,
            tools=[web_search],
        
        )
    logging.info("Done build search agent")

except Exception as e:
    raise multi_agent(e,sys)

################


try:
    logging.info("building reader agent .....")

    # 2nd Agent : Reader Agent
    def build_reader_agent():
        return create_agent(
            model= llm,
            tools=[scrape_url],

        )
    logging.info("Done build reader agent")

except Exception as e:
    raise multi_agent(e,sys)


try:
    logging.info("Loading prompt configurations from YAML file...")
    
    config_path = "config/prompts.yaml"
    with open(config_path, "r", encoding="utf-8") as file:
        prompts_config = yaml.safe_load(file)

    logging.info("Successfully loaded prompts configuration.")

    # ── Writer Chain ──────────────────────────────────────
    writer_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts_config["writer_prompt"]["system"]),
        ("human", prompts_config["writer_prompt"]["human"]),
    ])
    writer_chain = writer_prompt | llm | StrOutputParser()

    # ── Critic Chain ──────────────────────────────────────
    critic_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts_config["critic_prompt"]["system"]),
        ("human", prompts_config["critic_prompt"]["human"]),
    ])
    critic_chain = critic_prompt | llm | StrOutputParser()

    logging.info("Successfully initialized Writer and Critic chains.")

except Exception as e:
    logging.debug("Error while loading YAML prompt configurations or initializing chains.")
    raise multi_agent(e, sys)

