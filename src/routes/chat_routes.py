import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models.requests.chat_request import ChatRequest
from models.responses.base_response import BaseResponse
from services import chat_service

router = APIRouter(tags=["Chat"])

@router.post("/chat/", response_model=BaseResponse, summary="Generate complete chat response")
def chat(request: ChatRequest):
    """
    Generate a complete chat response based on the given prompt.

    Args:
        request (ChatRequest): The chat request containing the prompt.

    Returns:
        BaseResponse: The complete chat response wrapped in a BaseResponse.
    """
    try:
        data =  chat_service.chat_generate(request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return BaseResponse(data=data.content)

@router.post("/chat/stream", summary="Stream chat response", response_model_exclude_unset=True)
async def chat_stream(request: ChatRequest):
    """
    Stream a chat response based on the given prompt for real-time updates.

    Args:
        request (ChatRequest): The chat request containing the prompt.

    Returns:
        StreamingResponse: A stream of the generated chat response.
    """
    try:
        stream = chat_service.chat_generate_stream(request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    async def event_generator():
        for chunk in stream:
            chunk_dict = json.loads(chunk.model_dump_json()) 
            response = BaseResponse(data=chunk_dict).model_dump()
            yield f"{json.dumps(response, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(event_generator(), media_type='text/event-stream')


@router.get("/get-model-info/", response_model=BaseResponse, summary="Retrieve model information")
async def get_model_info():
    """
    Retrieve information about the currently loaded chat model.

    Returns:
        BaseResponse: A response containing the model information.
    """
    try:
        data = await chat_service.get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return BaseResponse(data=data)
