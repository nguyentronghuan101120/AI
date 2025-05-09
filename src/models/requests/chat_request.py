from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: list[dict]
    has_file: bool = False
    chat_session_id: str | None = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": [{"role": "user", "content": "Hello, how are you?"}],
                    "has_file": False,
                    "chat_session_id": "123"
                }
            ]
        }
    }