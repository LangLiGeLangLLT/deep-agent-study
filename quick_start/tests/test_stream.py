import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from quick_start.agents.research_agent import agent
from langchain.messages import AIMessageChunk, ToolMessage

# for chunk in agent.stream(
#     {"messages": [{"role": "user", "content": "What is langgraph?"}]},
#     stream_mode="updates",
#     subgraphs=True,
#     version="v2",
# ):
#     if chunk["type"] == "updates":
#         # Check if this event came from a subagent
#         is_subagent = any(segment.startswith("tools:") for segment in chunk["ns"])

#         if is_subagent:
#             # Extract the tool call ID from the namespace
#             tool_call_id = next(
#                 s.split(":")[1] for s in chunk["ns"] if s.startswith("tools:")
#             )
#             print(f"Subagent {tool_call_id}: {chunk['data']}")
#         else:
#             print(f"Main agent: {chunk['data']}")

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
        source = (
            next((s for s in chunk["ns"] if s.startswith("tools:")), "main")
            if is_subagent
            else "main"
        )

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
            print(
                f"\n[{source}] Tool result [{token.name}]: {str(token.content)[:150]}"
            )

        # Regular AI content (skip tool call messages)
        if (
            isinstance(token, AIMessageChunk)
            and token.content
            and not token.tool_call_chunks
        ):
            print(token.content, end="", flush=True)

print()
