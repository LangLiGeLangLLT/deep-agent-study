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
