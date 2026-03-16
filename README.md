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

model = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0,
)
```
