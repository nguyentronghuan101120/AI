import torch
from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion import (
    StableDiffusionPipeline,
)
from constants.config import IMAGE_MODEL_ID_OR_LINK, TORCH_DEVICE
from utils.timing import measure_time

torch.backends.cuda.matmul.allow_tf32 = True  # Enable TF32 for performance on CUDA

pipeline = None


def load_pipeline():
    global pipeline
    with measure_time("Load image pipeline"):
        pipeline = StableDiffusionPipeline.from_pretrained(
            IMAGE_MODEL_ID_OR_LINK,
            torch_dtype=torch.bfloat16,
            variant="fp16",
            # safety_checker=True,
            use_safetensors=True,
        )


def clear_resources():
    global pipeline
    pipeline = None
