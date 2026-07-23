
---

**4. `config/settings.py`**
```python
import os
from dotenv import load_dotenv

load_dotenv()

XAPI_KEY = os.getenv("XAPI_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not XAPI_KEY:
    raise ValueError("XAPI_KEY is not set in .env file")

LLM_CONFIG = {
    "model": "gpt-4o",
    "temperature": 0.2,
    "api_key": XAPI_KEY
}