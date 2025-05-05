from pydantic import BaseModel

from models.requests.file_request import FileRequest

class ChatRequest(BaseModel):
    prompt: list[dict]
    hasTool: bool = True
    file: FileRequest
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": [{"role": "user", "content": "Hello, how are you?"}],
                    "file": {
                        "file_id": "123",
                        "file_type": "pdf"
                    }
                }
            ]
        }
    }