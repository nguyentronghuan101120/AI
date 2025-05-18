# import torch
# from diffusers import StableDiffusionPipeline
# from constants.config import IMAGE_MODEL_ID_OR_LINK, TORCH_DEVICE

# torch.backends.cuda.matmul.allow_tf32 = True  # Enable TF32 for performance on CUDA

# _pipeline = None

# def get_pipeline() -> StableDiffusionPipeline:
#     global _pipeline
#     if _pipeline is None:
#         try:
#             _pipeline = StableDiffusionPipeline.from_pretrained(
#                 IMAGE_MODEL_ID_OR_LINK,
#                 torch_dtype=torch.bfloat16,
#                 variant="fp16",
#                 # safety_checker=True,
#                 use_safetensors=True,
#             )
#             # _pipeline = StableDiffusionPipeline.from_single_file(
#             #     IMAGE_MODEL_ID_OR_LINK,
#             #     torch_dtype=torch.bfloat16,
#             #     variant="fp16",
#             #     # safety_checker=True,
#             #     use_safetensors=True,
#             # )
#             _pipeline.to(TORCH_DEVICE)
#         except Exception as e:
#             raise RuntimeError(f"Failed to load the model: {e}")
#     return _pipeline

# pipeline = get_pipeline()
