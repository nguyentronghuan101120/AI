from typing import List, Optional
from pydantic import BaseModel

from constants.config import MODEL_NAME
from models.others.message import Role, Message


class ChatRequest(BaseModel):
    messages: List[Message]
    has_file: bool = False
    chat_session_id: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "has_file": False,
                    "chat_session_id": "123",
                    "messages": [{"role": Role.user, "content": "hello"}],
                }
            ]
        }
    }
