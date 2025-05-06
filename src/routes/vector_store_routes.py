import json
import uuid
from fastapi import APIRouter
from models.requests.chat_request import ChatRequest
from models.responses.base_exception_response import BaseExceptionResponse
from models.responses.base_response import BaseResponse
from services import  vector_store_service
from utils.client import openai_client
import os
from chromadb import PersistentClient


router = APIRouter(tags=["Vector Store"])

@router.get("/vector-store/get-all-ids", summary="Get all vector store IDs")
async def get_vector_stores():
    """
    Get all vector store IDs from the data directory.
    
    Returns:
        BaseResponse: List of vector store IDs
    """
    try:
        collections = vector_store_service.get_all_collections_id()
        return BaseResponse(data=[collections])
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))

@router.post('/vector-store/inspect-collection', summary="Inspect a vector store collection")
async def inspect_collection(collection_id: str):
    """
    Inspect a vector store collection.
    """
    try:
        results = vector_store_service.inspect_collection(collection_id)
        return BaseResponse(data=results)
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))
