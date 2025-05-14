import os
import time
from constants.config import OUTPUT_DIR
from utils import image_pipeline

negative_promt = "blurry, distorted, pixelated, incomplete, poorly drawn, misaligned, weird proportions, bad perspective, unnatural colors, noisy, out of focus, glitchy, unsharp, overexposed, underexposed, poorly lit, bad composition, excessive noise, oversaturated, too dark, too bright, inconsistent lighting, discolored, overly stylized, unrealistic, awkward pose, unbalanced, mismatched, distorted features, flat, unnatural texture, chaotic, unreadable, incoherent, asymmetrical, low quality, lowres, wrong anatomy, bad anatomy, deformed, disfigured, ugly"
width = 512
height = 512
guidance_scale = 7.5
num_inference_steps = 30

base_url = "http://0.0.0.0:7860"

def generate_image_url(prompt: str) -> str:
    """
    Creates an image based on the specified prompt using DiffusionPipeline
    :param prompt: The prompt used for generate the image (must be in English)
    :output: URL of the new image
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        image = image_pipeline.pipeline(
            prompt=prompt,
            negative_prompt=negative_promt,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
        ).images[0]

        file_name = f"image_{int(time.time())}.png"
        image_path = os.path.join(OUTPUT_DIR, file_name)
        image.save(image_path)

        return f"{base_url}/{OUTPUT_DIR}/{file_name}"
    except Exception as e:
        raise RuntimeError(f"Failed to generate image: {e}")
