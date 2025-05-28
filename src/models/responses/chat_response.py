from typing import Any, List, Optional
from click import argument
from pydantic import BaseModel
from models.others.message import Message, Role
from models.responses.tool_call_response import ToolCall


class Choice(BaseModel):
    message: Optional[Message] = None
    delta: Optional[Message] = None
    function_call: Optional[ToolCall] = None


class ChatResponse(BaseModel):
    id: Optional[str] = None
    choices: Optional[List[Choice]] = None

    @classmethod
    def from_stream_chunk(cls, chunk: dict, last_role: Optional[Role] = None):
        choices = []
        updated_role = last_role  # Default to last role

        for choice in chunk.get("choices", []):
            delta_data = choice.get("delta", {})

            # Skip chunks that contain neither content nor role
            if not delta_data.get("content") and not delta_data.get("role"):
                continue

            # Determine role
            if "role" in delta_data and delta_data["role"] is not None:
                try:
                    updated_role = Role(delta_data["role"])
                except ValueError:
                    # Skip or log invalid role values
                    continue

            if not updated_role:
                # Still no role available, skip
                continue

            message = Message(
                role=updated_role,
                content=delta_data.get("content"),
            )

            choices.append(
                Choice(
                    message=message,
                    delta=message,
                )
            )

        return (
            cls(
                id=chunk.get("id"),
                choices=choices,
            ),
            updated_role,
        )

    @classmethod
    def from_llm_output(cls, output: dict) -> "ChatResponse":
        """
        Map the output dict from llm.create_chat_completion to a ChatResponse instance.
        """
        choices = []
        for choice in output.get("choices", []):
            message_data = choice.get("message", {})
            tool_calls_data = message_data.get("tool_calls")
            tool_calls = None
            if tool_calls_data:
                tool_calls = [ToolCall(**tc) for tc in tool_calls_data]
            message = Message(
                role=Role(message_data["role"]),
                content=message_data.get("content"),
                tool_calls=tool_calls,
            )
            # function_call is for OpenAI compatibility, may be None
            function_call = None
            if "function_call" in choice:
                function_call = ToolCall(**choice["function_call"])
            choices.append(
                Choice(
                    message=message,
                    function_call=function_call,
                )
            )
        return cls(
            id=output.get("id"),
            choices=choices,
        )
