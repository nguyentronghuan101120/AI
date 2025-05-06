import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from constants.file_type import FileType
from models.responses.base_exception_response import BaseExceptionResponse
from models.responses.base_response import BaseResponse
from services.process_file_service import save_file, splitter_and_save_to_database

router = APIRouter(tags=["Process File"])

@router.post("/upload-and-process-file", summary="Upload and process file")
async def upload_file(file: UploadFile = File(...), chat_session_id: str | None = None):
    """
    Upload a file and extract its content based on file type.
    Supported file types: PDF, DOCX, PNG, JPG, JPEG, MP4, MOV

    Args:
        file (UploadFile): The file to upload

    Returns:
        JSONResponse: The extracted content from the file
    """
    try:
        
        if(chat_session_id is None):
            chat_session_id = str(uuid.uuid4())
        
        file_id, ext = save_file(file)
        
        splitter_and_save_to_database(file_id, ext, chat_session_id)
        
        return BaseResponse(message="File uploaded successfully", data=chat_session_id)
        
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))
