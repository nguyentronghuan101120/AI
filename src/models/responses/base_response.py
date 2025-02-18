from typing import Any, Optional

from pydantic import BaseModel

class BaseResponse(BaseModel):
    status_code: Optional[int] = 200
    message: Optional[str] = "Success"
    data: Optional[Any] = None

    # def __init__(self, status_code: Optional[int] = 200, message: Optional[str] = "Success", data: Optional[Any] = None):
    #     self.status_code = status_code
    #     self.message = message
    #     self.data = data