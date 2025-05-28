from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from models.responses.tool_call_response import ToolCall


class Role(str, Enum):
    assistant = "assistant"
    user = "user"
    system = "system"
    tool = "tool"


class Message(BaseModel):
    role: Role
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

    def to_map(self):
        data = self.model_dump(exclude_none=True)
        data["role"] = self.role.value
        return data
