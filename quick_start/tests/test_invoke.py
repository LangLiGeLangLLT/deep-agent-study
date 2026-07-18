import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from quick_start.agents.research_agent import agent

result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})

print(f"[Final answer]: {result['messages'][-1].content}")
