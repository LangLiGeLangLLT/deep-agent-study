import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent
from langchain.messages import AIMessage, ToolMessage

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


# `create_deep_agent` provides `write_todos` by default. This prompt makes the
# planning and execution phases explicit and keeps the agent from skipping the plan.
research_instructions = """You are an expert researcher using a plan-and-execute workflow.

For every request, follow these phases in order:

## Plan
1. Use `write_todos` to create a short, concrete checklist.
2. Make each todo independently verifiable and put the most useful steps first.

## Execute
1. Work through the checklist one item at a time.
2. Mark the current item in progress before starting it and mark it completed immediately after it succeeds.
3. Use `internet_search` whenever a step needs current or external information.
4. If a step fails, revise the remaining checklist before continuing.

## Complete
After all feasible todos are complete, provide a concise answer that distinguishes
verified findings from assumptions. Do not claim that work was completed unless the
corresponding todo is marked complete.

## `internet_search`
Use this tool to search the web. It accepts `query`, `max_results`, `topic`, and
`include_raw_content`.
"""

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions,
)

final_answer = ""

for chunk in agent.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "请先使用 write_todos 制定计划，再执行以下研究：比较 LangGraph、"
                    "LangChain Agents 和 CrewAI 的定位、核心能力与适用场景，最后给出结论。"
                ),
            }
        ]
    },
    stream_mode="updates",
    version="v2",
):
    if chunk["type"] != "updates":
        continue

    for node_update in chunk["data"].values():
        if not isinstance(node_update, dict):
            continue
        messages = node_update.get("messages", [])
        messages = getattr(messages, "value", messages)
        if not isinstance(messages, (list, tuple)):
            messages = [messages]

        for message in messages:
            if isinstance(message, AIMessage):
                for tool_call in message.tool_calls:
                    if tool_call["name"] == "write_todos":
                        print("\n[TODO update]")
                        print(tool_call["args"].get("todos", tool_call["args"]))
                if message.content and not message.tool_calls:
                    final_answer = message.content
            elif isinstance(message, ToolMessage) and message.name == "write_todos":
                print("[TODO state]")
                print(message.content)

print("\n[Final answer]")
print(final_answer)
