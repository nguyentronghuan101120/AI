import base64
import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.requests.image_request import ImageRequest
from models.responses.base_response import BaseResponse
from services import image_service

router = APIRouter(tags=["Image"])

@router.post("/generate/")
async def generate_image(imgRequest: ImageRequest):
    """
    Generate and return an image as a PNG stream.
    
    Args:
        imgRequest (ImageRequest): The request containing image generation parameters
        
    Returns:
        StreamingResponse: A streaming response containing the generated PNG image
    """
    image = await image_service.generate_image(imgRequest=imgRequest)
    memory_stream = io.BytesIO()
    image.save(memory_stream, format="PNG")
    memory_stream.seek(0)
    return StreamingResponse(memory_stream, media_type="image/png")

@router.post("/generatebase64/") 
async def generate_base64_image(imgRequest: ImageRequest):
    """
    Generate an image and return it as a base64 encoded JPEG string.
    
    Args:
        imgRequest (ImageRequest): The request containing image generation parameters
        
    Returns:
        dict: A dictionary containing the base64 encoded image string under the 'image' key
    """
    image = await image_service.generate_image(imgRequest=imgRequest)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return BaseResponse(data={"image": img_str})

@router.post("/image/url-generator/")
async def generate_image_url(prompt: str, width: int = 512, height: int = 512, guidance_scale: float = 7.5, num_inference_steps: int = 30):
    image_url = image_service.generate_image_url(prompt, width, height, guidance_scale, num_inference_steps)
    return BaseResponse(data={"image": image_url})



