# Device setup
import torch

# Check for Apple Silicon
IS_APPLE_SILICON = torch.backends.mps.is_available()
IS_CUDA_AVAILABLE = torch.cuda.is_available()

# Set device priority: CUDA > MPS > CPU
TORCH_DEVICE = "cuda" if IS_CUDA_AVAILABLE else "mps" if IS_APPLE_SILICON else "cpu"

# Enable quantization for CPU/MPS
USE_QUANT = IS_CUDA_AVAILABLE

# Model optimization settings
MODEL_OPTIMIZATION = {
    "use_cache": True,
    "low_cpu_mem_usage": True,
    "torch_dtype": torch.float16 if IS_APPLE_SILICON else torch.float32,
}

IMAGE_MODEL_ID_OR_LINK = "stable-diffusion-v1-5/stable-diffusion-v1-5"
LLM_MODEL_NAME = "NousResearch/Hermes-2-Pro-Llama-3-8B"
CACHE_DIR = "/tmp/cache"
VECTOR_STORE_DIR = "/tmp/vector_store"
# EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
UPLOAD_DIR = "/tmp/uploads"
OUTPUT_DIR = "/tmp/outputs"
# FILE_NAME = "super-lite-model.gguf"
GGUF_FILE_NAME = "llama-3.1-8b-instruct-q4_k_m.gguf"
# FILE_NAME = "Phi-3.5-mini-instruct.IQ1_S.gguf"
GGUF_REPO_ID = "modularai/Llama-3.1-8B-Instruct-GGUF"
# REPO_ID = "MaziyarPanahi/Phi-3.5-mini-instruct-GGUF"
