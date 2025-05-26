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
VECTOR_STORE_DIR = "/tmp/vector_store"
# EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
UPLOAD_DIR = "/tmp/uploads"
OUTPUT_DIR = "/tmp/outputs"
# FILE_NAME = "super-lite-model.gguf"
FILE_NAME = "llama-3.1-8b-instruct-q4_k_m.gguf"
# FILE_NAME = "Phi-3.5-mini-instruct.IQ1_S.gguf"
REPO_ID = "modularai/Llama-3.1-8B-Instruct-GGUF"
# REPO_ID = "MaziyarPanahi/Phi-3.5-mini-instruct-GGUF"
