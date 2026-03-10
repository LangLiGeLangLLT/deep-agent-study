```bash


pip freeze > requirements.txt

pip install -r requirements.txt
```

```bash
uv init
uv add deepagents tavily-python
uv sync
```

```bash
uv add jupyter
uv add python-dotenv
uv add langchain-openai
```

```python
from dotenv import load_dotenv

load_dotenv()
```

```python
ChatOpenAI(model="Qwen/Qwen3-8B")
```

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="qwen3-max-2026-01-23",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0,
)
```
