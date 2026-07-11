import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

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

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions,
)

# result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})

# # Print the agent's response
# print(result["messages"][-1].content)

from langchain.messages import AIMessageChunk, ToolMessage

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is langgraph?"}]},
    stream_mode="messages",
    subgraphs=True,
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]

        # Identify source: "main" or the subagent namespace segment
        is_subagent = any(s.startswith("tools:") for s in chunk["ns"])
        source = next((s for s in chunk["ns"] if s.startswith("tools:")), "main") if is_subagent else "main"

        # Tool call chunks (streaming tool invocations)
        if isinstance(token, AIMessageChunk) and token.tool_call_chunks:
            for tc in token.tool_call_chunks:
                if tc.get("name"):
                    print(f"\n[{source}] Tool call: {tc['name']}")
                # Args stream in chunks - write them incrementally
                if tc.get("args"):
                    print(tc["args"], end="", flush=True)

        # Tool results
        if isinstance(token, ToolMessage):
            print(f"\n[{source}] Tool result [{token.name}]: {str(token.content)[:150]}")

        # Regular AI content (skip tool call messages)
        if (
            isinstance(token, AIMessageChunk)
            and token.content
            and not token.tool_call_chunks
        ):
            print(token.content, end="", flush=True)

print()