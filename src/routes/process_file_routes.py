from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from constants.file_type import FileType
from models.responses.base_exception_response import BaseExceptionResponse
from models.responses.base_response import BaseResponse
from services.process_file_service import save_file, splitter_and_save_to_database

router = APIRouter(tags=["Process File"])

@router.post("/upload", summary="Upload and process file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and extract its content based on file type.
    Supported file types: PDF, DOCX, PNG, JPG, JPEG, MP4, MOV

    Args:
        file (UploadFile): The file to upload

    Returns:
        JSONResponse: The extracted content from the file
    """
    try:
        file_id, ext = save_file(file)
        
        return BaseResponse(message="File uploaded successfully", data={
            "file_id": file_id,
            "file_type": ext
        })
        
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))
    
@router.get("/process-file", summary="Process file")
async def process_file(file_id: str, file_type: FileType):
    """
    Process a file based on its ID.
    """     
    try:
        splitter_and_save_to_database(file_id, file_type)
        return BaseResponse(message="File processed successfully")
    except Exception as e:
        raise BaseExceptionResponse(message=str(e))