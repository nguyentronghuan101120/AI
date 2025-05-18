from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Role(str, Enum):
    assistant = "assistant"
    user = "user"
    system = "system"
    tool = "tool"


class Message(BaseModel):
    role: Role
    content: Optional[str] = None

    def to_map(self):
        return {
            "role": self.role.value,
            "content": self.content,
        }
