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
LLM_MODEL_NAME = "NousResearch/Hermes-3-Llama-3.1-8B" 
CACHE_DIR = "/tmp/cache"
VECTOR_STORE_DIR = "/tmp/vector_store"
# EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
UPLOAD_DIR = "/tmp/uploads"
OUTPUT_DIR = "/tmp/outputs"
GGUF_REPO_ID = "NousResearch/Hermes-3-Llama-3.1-8B-GGUF"
GGUF_FILE_NAME = "Hermes-3-Llama-3.1-8B.Q4_K_M.gguf"
