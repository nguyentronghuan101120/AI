from typing import Optional
from pydantic import BaseModel


class FunctionOfToolCall(BaseModel):
    name: Optional[str]
    arguments: Optional[str]


class ToolCall(BaseModel):
    id: Optional[str]
    type: Optional[str]
    function: Optional[FunctionOfToolCall]
