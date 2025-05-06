import json
import uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.requests.chat_request import ChatRequest
from models.responses.base_exception_response import BaseExceptionResponse
from models.responses.base_response import BaseResponse
from services import chat_service
from services.process_file_service import get_file_content

router = APIRouter(tags=["Chat"])

@router.post("/chat/stream", summary="Stream chat response", response_model_exclude_unset=True)
def chat_stream(request: ChatRequest):
    """
    Stream a chat response based on the given prompt for real-time updates.

    Args:
        request (ChatRequest): The chat request containing the prompt.

    Returns:
        StreamingResponse: A stream of the generated chat response.
    """
    try:
        if(request.chat_session_id is None):
            request.chat_session_id = str(uuid.uuid4())
        
        stream = chat_service.chat_generate_stream(request=request)
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))
    
    def event_generator():
        for chunk in stream:
            chunk_dict = json.loads(chunk.model_dump_json()) 
            response = BaseResponse(data=chunk_dict).model_dump()
            yield f"{json.dumps(response, ensure_ascii=False)}\n\n"
    return StreamingResponse(event_generator(), media_type='text/event-stream')

@router.post("/chat", summary="Non-streaming chat response", response_model_exclude_unset=True)
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
        return BaseResponse(data=json.loads(response.model_dump_json()))
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))
