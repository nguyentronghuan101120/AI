# Device setup
import torch

TORCH_DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)
IMAGE_MODEL_ID_OR_LINK = "stable-diffusion-v1-5/stable-diffusion-v1-5"
MODEL_NAME = "facebook/opt-125m"
CACHE_DIR = "/tmp/cache"
DATA_DIR = "/tmp/data"
EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
# EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
UPLOAD_DIR = "/tmp/uploads"
OUTPUT_DIR = "/tmp/outputs"
# FILE_NAME = "super-lite-model.gguf"
FILE_NAME = "llama_3.1_8b_instruct_q4_k_m.gguf"
# FILE_NAME = "Qwen2.5-7B-Instruct-1M-Q4_K_M.gguf"
