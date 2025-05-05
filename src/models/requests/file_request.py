from pydantic import BaseModel

from constants.file_type import FileType

class FileRequest(BaseModel):
    file_id: str
    file_type: FileType
    
    