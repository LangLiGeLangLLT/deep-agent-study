import os

from dotenv import load_dotenv

from langgraph.checkpoint.memory import InMemorySaver

from daytona import Daytona, DaytonaConfig
from langchain_daytona import DaytonaSandbox

load_dotenv()

config = DaytonaConfig(api_key=os.getenv("DAYTONA_API_KEY"))

sandbox = Daytona(config=config).create()
backend = DaytonaSandbox(sandbox=sandbox)

result = backend.execute("echo ready")
print(result)

import csv
import io

# Create sample sales data
data = [
    ["Date", "Product", "Units Sold", "Revenue"],
    ["2025-08-01", "Widget A", 10, 250],
    ["2025-08-02", "Widget B", 5, 125],
    ["2025-08-03", "Widget A", 7, 175],
    ["2025-08-04", "Widget C", 3, 90],
    ["2025-08-05", "Widget B", 8, 200],
]

# Convert to CSV bytes
text_buf = io.StringIO()
writer = csv.writer(text_buf)
writer.writerows(data)
csv_bytes = text_buf.getvalue().encode("utf-8")
text_buf.close()

# Upload to backend
backend.upload_files([("/home/daytona/data/sales_data.csv", csv_bytes)])
print("File uploaded successfully.")

from langchain.tools import tool


@tool(parse_docstring=True)
def send_message(text: str, file_path: str | None = None) -> str:
    """Send message, optionally including attachments such as images.

    Args:
        text: (str) text content of the message
        file_path: (str) file path of the attachment in the filesystem.
    """
    return f"Message sent. Text: {text}, File: {file_path}"


from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain_core.utils.uuid import uuid7

model = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0,
)

checkpointer = InMemorySaver()

agent = create_deep_agent(
    model=model, tools=[send_message], backend=backend, checkpointer=checkpointer
)

thread_id = str(uuid7())
config = {"configurable": {"thread_id": thread_id}}

input_message = {
    "role": "user",
    "content": """\
Analyze /home/daytona/data/sales_data.csv in the current dir and generate a beautiful plot.
When finished, send your analysis and the plot using the tool.
""",
}

for step in agent.stream(
    {"messages": [input_message]},
    config=config,
    stream_mode="updates",
):
    for _, update in step.items():
        if (
            update
            and (messages := update.get("messages"))
            and isinstance(messages, list)
        ):
            for message in messages:
                message.pretty_print()
