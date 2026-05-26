import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0,
)

from deepagents import create_deep_agent
from tavily import TavilyClient
from langchain_core.messages import HumanMessage

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def internet_search(query: str, max_results: int = 5) -> dict:
    """搜索互联网获取最新信息。"""
    return tavily_client.search(query, max_results=max_results)


agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt="""\
你是一位专业的技术研究员。
面对复杂研究任务时，你会：
1. 先用 write_todos 制定研究计划
2. 逐步执行每个步骤，及时更新进度
3. 将搜索结果写入文件系统整理
4. 最终输出完整的研究报告
""",
)

result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="请调研 Agent 开发领域的三大 Harness 框架（Deep Agents、Claude Agent SDK、Codex SDK），对比它们的核心能力差异，写一份简要分析报告。"
            )
        ]
    }
)


def obj_to_dict(obj):
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


import json

print(json.dumps(result["messages"], default=obj_to_dict, indent=2, ensure_ascii=False))
print(result["messages"][-1].content)
