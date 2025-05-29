from typing import List, Optional
from pydantic import BaseModel

from constants.config import LLM_MODEL_NAME


class ChatRequest(BaseModel):
    messages: List[dict]
    has_file: bool = False
    chat_session_id: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "has_file": False,
                    "chat_session_id": "123",
                    "messages": [{"role": 'user', "content": "hello"}],
                }
            ]
        }
    }
