from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: list[dict]
    hasFile: bool = False
    chat_session_id: str | None = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": [{"role": "user", "content": "Hello, how are you?"}],
                    "hasFile": False,
                    "chat_session_id": "123"
                }
            ]
        }
    }