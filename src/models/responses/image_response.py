
from pydantic import BaseModel


class APIResponse(BaseModel):
    image: str # base64 of image