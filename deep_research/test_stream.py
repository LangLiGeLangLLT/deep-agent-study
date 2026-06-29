from langchain.messages import HumanMessage
from agent import agent

messages = [HumanMessage(content="What is deepagents?")]

for chunk in agent.stream(
    {"messages": messages},
    stream_mode="updates",
    subgraphs=True,
    version="v2",
):
    if chunk["type"] == "updates":
        # Check if this event came from a subagent
        is_subagent = any(segment.startswith("tools:") for segment in chunk["ns"])

        if is_subagent:
            # Extract the tool call ID from the namespace
            tool_call_id = next(
                s.split(":")[1] for s in chunk["ns"] if s.startswith("tools:")
            )
            if chunk.get("data", {}).get("model"):
                model_messages = (
                    chunk.get("data", {}).get("model", {}).get("messages", [])
                )
                for message in model_messages:
                    if message.content:
                        print(
                            f"\n=============== Subagent {tool_call_id} model message ===============\n"
                        )
                        print(message.content[:200])
            if chunk.get("data", {}).get("tools"):
                tool_messages = (
                    chunk.get("data", {}).get("tools", {}).get("messages", [])
                )
                for message in tool_messages:
                    if message.content:
                        print(
                            f"\n=============== Subagent {tool_call_id} tool message ===============\n"
                        )
                        print(message.content[:200])
        else:
            if chunk.get("data", {}).get("model"):
                model_messages = (
                    chunk.get("data", {}).get("model", {}).get("messages", [])
                )
                for message in model_messages:
                    if message.content:
                        print(
                            f"\n=============== Main agent model message ===============\n"
                        )
                        print(message.content[:200])
            if chunk.get("data", {}).get("tools"):
                tool_messages = (
                    chunk.get("data", {}).get("tools", {}).get("messages", [])
                )
                for message in tool_messages:
                    if message.content:
                        print(
                            f"\n=============== Main agent tool message ===============\n"
                        )
                        print(message.content[:200])
