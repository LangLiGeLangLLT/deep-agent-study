import os

from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv

load_dotenv()


from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

model = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0,
)

from typing import Literal
from langchain.tools import tool
from pathlib import Path

EXAMPLE_DIR = Path(__file__).parent


@tool
def web_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news"] = "general",
) -> dict:
    """Search the web for current information.

    Args:
        query: The search query (be specific and detailed)
        max_results: Number of results to return (default: 5)
        topic: "general" for most queries, "news" for current events

    Returns:
        Search results with titles, URLs, and content excerpts.
    """
    try:
        from tavily import TavilyClient

        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return {"error": "TAVILY_API_KEY not set"}

        client = TavilyClient(api_key=api_key)
        return client.search(query, max_results=max_results, topic=topic)
    except Exception as e:
        return {"error": f"Search failed: {e}"}


@tool
def generate_cover(prompt: str, slug: str) -> str:
    """Generate a cover image for a blog post.

    Args:
        prompt: Detailed description of the image to generate.
        slug: Blog post slug. Image saves to blogs/<slug>/hero.png
    """
    try:
        output_path = EXAMPLE_DIR / "blogs" / slug / "hero.png"
        return f"Image saved to {output_path}"
    except Exception as e:
        return f"Error: {e}"


@tool
def generate_social_image(prompt: str, platform: str, slug: str) -> str:
    """Generate an image for a social media post.

    Args:
        prompt: Detailed description of the image to generate.
        platform: Either "linkedin" or "tweets"
        slug: Post slug. Image saves to <platform>/<slug>/image.png
    """
    try:
        output_path = EXAMPLE_DIR / platform / slug / "image.png"
        return f"Image saved to {output_path}"
    except Exception as e:
        return f"Error: {e}"


agent = create_deep_agent(
    model=model,
    memory=["./AGENTS.md"],
    skills=["./skills/"],
    tools=[generate_cover, generate_social_image],
    backend=FilesystemBackend(root_dir=EXAMPLE_DIR, virtual_mode=True),
    subagents=[
        {
            "name": "researcher",
            "description": """\
ALWAYS use this first to research any topic before writing content.
Searches the web for current information, statistics, and sources.
When delegating, tell it the topic AND the file path to save results
(e.g., 'Research renewable energy and save to research/renewable-energy.md').
""",
            "system_prompt": """\
You are a research assistant. You have access to web_search and write_file tools.

## Your Tools
- web_search(query, max_results=5, topic="general") - Search the web
- write_file(file_path, content) - Save your findings

## Your Process
1. Use web_search to find information on the topic
2. Make 2-3 targeted searches with specific queries
3. Gather key statistics, quotes, and examples
4. Save findings to the file path specified in your task

## Important
- The user will tell you WHERE to save the file - use that exact path
- Always include source URLs in your findings
- Keep findings concise but informative
""",
            "tools": [web_search],
        }
    ],
)

result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="Write a blog post about how AI agents are transforming software development"
            )
        ],
    },
    config={"configurable": {"thread_id": "content-builder-demo"}},
)

for msg in result.get("messages", []):
    if hasattr(msg, "content") and msg.content:
        print(msg.content)
