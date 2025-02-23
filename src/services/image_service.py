import os
import time
import torch
from PIL.Image import Image
from utils import image_pipeline

from models.requests.image_request import ImageRequest
# from diffusers import BitsAndBytesConfig, SD3Transformer2DModel

async def generate_image(imgRequest: ImageRequest) -> Image:

    try:
        # Generate image based on input request
        return image_pipeline.pipeline(
            prompt=imgRequest.prompt,
            negative_prompt=imgRequest.negative_prompt,
            width=imgRequest.width,
            height=imgRequest.height,
            guidance_scale=imgRequest.guidance_scale,
            num_inference_steps=imgRequest.num_inference_steps,
            # generator=torch.Generator(device=device).manual_seed(-1)
        ).images[0]
    except Exception as e:
        raise RuntimeError(f"Failed to generate image: {e}")
    
def generate_image_url(prompt: str, width: int = 512, height: int = 512, guidance_scale: float = 7.5, num_inference_steps: int = 30) -> str:
    """
    Creates an image based on the specified prompt using DiffusionPipeline
    :param prompt: The prompt used for generate the image (must be in English)
    :param width: The width of the generated image
    :param height: The height of the generated image
    :param guidance_scale: The guidance scale for image generation
    :param num_inference_steps: The number of inference steps
    :output: URL of the new image
    """
    # Ensure the outputs directory exists
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    try:
        image = image_pipeline.pipeline(
            prompt=prompt,
            negative_prompt='blurry, distorted, pixelated, incomplete, poorly drawn, misaligned, weird proportions, bad perspective, unnatural colors, noisy, out of focus, glitchy, unsharp, overexposed, underexposed, poorly lit, bad composition, excessive noise, oversaturated, too dark, too bright, inconsistent lighting, discolored, overly stylized, unrealistic, awkward pose, unbalanced, mismatched, distorted features, flat, unnatural texture, chaotic, unreadable, incoherent, asymmetrical, low quality, lowres, wrong anatomy, bad anatomy, deformed, disfigured, ugly',
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            # generator=torch.Generator(device=device).manual_seed(-1)
        ).images[0]

        file_name = f"image_{int(time.time())}.png"
        image.save("outputs/" + file_name) 
        return 'outputs/' + file_name
    except Exception as e:
        raise RuntimeError(f"Failed to generate image: {e}")
