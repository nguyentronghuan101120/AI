from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: list[dict]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": [{"role": "user", "content": "Hello, how are you?"}],
                }
            ]
        }
    }