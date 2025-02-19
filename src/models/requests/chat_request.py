from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: list[dict]
    hasTool: bool = True
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": [{"role": "user", "content": "Hello, how are you?"}],
                }
            ]
        }
    }