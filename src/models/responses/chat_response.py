from typing import Any, List, Optional
from pydantic import BaseModel
from models.others.message import Message, Role

# class Usage(BaseModel):
#     prompt_token: int
#     completion_token: int
#     total_tokens: int


class Choice(BaseModel):
    # index: int
    # logprobs: Any
    # finish_reason: Optional[str]
    message: Optional[Message] = None
    delta: Optional[Message] = None


class ChatResponse(BaseModel):
    id: Optional[str] = None
    # object: Optional[str] = None
    # created: Optional[int] = None
    # model: Optional[str] = None
    # system_fingerprint: Optional[str] = None
    # usage: Optional[Usage] = None
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
