import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent
from .middleware import DebugMiddleware
from langchain.agents.middleware import (
    ToolCallLimitMiddleware,
    ToolCallRequest,
    ToolRetryMiddleware,
    ToolErrorMiddleware,
)

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0,
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    raise ValueError("Internet search error!")
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""


def on_error(exc: Exception, request: ToolCallRequest) -> str | None:
    print(f"`{request.tool_call['name']}` failed with {type(exc).__name__}.")
    return f"`{request.tool_call['name']}` failed with {type(exc).__name__}."


agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions,
    middleware=[
        ToolRetryMiddleware(
            max_retries=2,
            backoff_factor=2.0,
            initial_delay=1.0,
        ),
        ToolCallLimitMiddleware(
            tool_name="internet_search",
            thread_limit=5,
            run_limit=3,
        ),
        ToolErrorMiddleware(on_error),
        DebugMiddleware(),
    ],
)
