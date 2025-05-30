import asyncio
import json
from typing import Dict
import uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.requests.cancel_chat_request import CancelChatRequest
from models.requests.chat_request import ChatRequest
from models.responses.base_exception_response import BaseExceptionResponse
from models.responses.base_response import BaseResponse
from services import chat_service

router = APIRouter(tags=["Chat"])

cancel_flags: Dict[str, bool] = {}


@router.post(
    "/chat/stream", summary="Stream chat response", response_model_exclude_unset=True
)
def chat_stream(request: ChatRequest):
    """
    Stream a chat response based on the given prompt for real-time updates.

    Args:
        request (ChatRequest): The chat request containing the prompt.

    Returns:
        StreamingResponse: A stream of the generated chat response.
    """
    try:
        stream = chat_service.chat_generate_stream(request=request)
        if request.chat_session_id is not None:
            cancel_flags[request.chat_session_id] = False
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))

    def event_generator():
        try:
            for chunk in stream:
                if request.chat_session_id and cancel_flags.get(request.chat_session_id, False):
                    break

                response = BaseResponse(data=chunk).model_dump()
                yield f"{json.dumps(response, ensure_ascii=False)}\n\n"
        finally:
            if request.chat_session_id is not None:
                cancel_flags.pop(request.chat_session_id, None)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post(
    "/chat", summary="Non-streaming chat response", response_model_exclude_unset=True
)
async def chat(request: ChatRequest):
    """
    Get a non-streaming chat response based on the given prompt.

    Args:
        request (ChatRequest): The chat request containing the prompt.

    Returns:
        BaseResponse: The complete chat response
    """
    if request.chat_session_id is None:
        request.chat_session_id = str(uuid.uuid4())

    try:
        response = chat_service.chat_generate(request=request)
        return BaseResponse(
            data=response,
        )
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))


@router.post("/chat/cancel")
async def cancel_stream(request: CancelChatRequest):
    if request.chat_session_id in cancel_flags:
        cancel_flags[request.chat_session_id] = True
        return BaseResponse(message="Cancelled")
    raise BaseExceptionResponse(status_code=404, message="Stream not found")
