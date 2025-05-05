# import torch
# from diffusers import StableDiffusionPipeline

# # Device setup
# _device = (
#     "cuda" if torch.cuda.is_available()
#     else "mps" if torch.backends.mps.is_available()
#     else "cpu"
# )
# torch.backends.cuda.matmul.allow_tf32 = True  # Enable TF32 for performance on CUDA
# _model_id_or_link = "stable-diffusion-v1-5/stable-diffusion-v1-5"

# _pipeline = None

# def get_pipeline() -> StableDiffusionPipeline:
#     global _pipeline
#     if _pipeline is None:
#         try:
#             _pipeline = StableDiffusionPipeline.from_pretrained(
#                 _model_id_or_link,
#                 torch_dtype=torch.bfloat16,
#                 variant="fp16",
#                 # safety_checker=True,
#                 use_safetensors=True,
#             )
#             # _pipeline = StableDiffusionPipeline.from_single_file(
#             #     _model_id_or_link,
#             #     torch_dtype=torch.bfloat16,
#             #     variant="fp16",
#             #     # safety_checker=True,
#             #     use_safetensors=True,
#             # )
#             _pipeline.to(_device)
#         except Exception as e:
#             raise RuntimeError(f"Failed to load the model: {e}")
#     return _pipeline

# pipeline = get_pipeline()
