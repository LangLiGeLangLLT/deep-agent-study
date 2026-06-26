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
                latest_model_message = (
                    chunk.get("data", {}).get("model", {}).get("messages", [])[-1]
                )
                if latest_model_message.content:
                    print(
                        f"\n\n=============== Subagent {tool_call_id} model message ===============\n\n"
                    )
                    print(latest_model_message.content)
        else:
            if chunk.get("data", {}).get("model"):
                latest_model_message = (
                    chunk.get("data", {}).get("model", {}).get("messages", [])[-1]
                )
                if latest_model_message.content:
                    print(
                        f"\n\n=============== Main agent model message ===============\n\n"
                    )
                    print(latest_model_message.content)
