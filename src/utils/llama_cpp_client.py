import os
import platform
import subprocess
from tabnanny import verbose
from typing import Generator, List
import llama_cpp
import torch
from constants.config import FILE_NAME, REPO_ID
from models.others.message import Message
from models.responses.chat_response import ChatResponse
from utils.timing import measure_time
from utils.tools import tools_define

# Determine number of CPU threads based on device
if torch.cuda.is_available() or (
    hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
):
    n_threads = os.cpu_count()  # Fewer threads if using GPU/MPS, adjust as needed
    n_gpu_layers = 20
else:
    n_threads = 2
    n_gpu_layers = 0

# llm = llama_cpp.Llama(
#     model_path=FILE_NAME,
#     n_threads=n_threads,
#     n_gpu_layers=n_gpu_layers,
#     n_ctx=4096,
#     # chat_format="chatml_function_calling",  # <-- important for tool/function calling
#     verbose=False,
# )


def detect_n_gpu_layers():
    system = platform.system()

    # ✅ macOS (Apple Silicon)
    if system == "Darwin" and platform.machine() in ["arm64", "arm"]:
        try:
            # Get total memory in GB
            mem_bytes = int(
                subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip()
            )
            mem_gb = mem_bytes / (1024**3)

            # Estimate usable VRAM for Metal backend (usually safe to use 4–6 GB)
            if mem_gb >= 16:
                return 32
            elif mem_gb >= 8:
                return 16
            else:
                return 8
        except Exception as e:
            print("⚠️ Failed to detect Apple memory:", e)
            return 0

    # ✅ Linux or Windows with NVIDIA GPU
    try:
        import torch

        if torch.cuda.is_available():
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)

            if vram >= 24:
                return 60
            elif vram >= 16:
                return 40
            elif vram >= 12:
                return 32
            elif vram >= 8:
                return 24
            elif vram >= 6:
                return 16
            elif vram >= 4:
                return 8
            else:
                return 0
    except ImportError:
        print("⚠️ torch not installed — cannot detect CUDA device")

    # ❌ Fallback: no GPU
    return 0

å
# Usage
n_gpu_layers = detect_n_gpu_layers()

llm = llama_cpp.Llama.from_pretrained(
    repo_id=REPO_ID,
    filename=FILE_NAME,
    n_threads=n_threads,
    n_gpu_layers=n_gpu_layers,
    n_ctx=4096,
    verbose=True,
)

print(f"🧠 Detected max GPU layers: {n_gpu_layers}")


def create(messages: List[Message], has_tool_call: bool = True):
    prompt = [message.to_map() for message in messages]

    tools = tools_define.tools if has_tool_call else None
    tool_choice = "auto" if has_tool_call else "none"

    print("Starting create chat completion")

    try:
        with measure_time("Starting create chat completion"):
            output = llm.create_chat_completion(
                prompt,
                tools=tools,
                tool_choice=tool_choice,
            )  # type: ignore
            return ChatResponse.from_llm_output(output)
    except Exception as e:
        print(f"Error in create chat completion: {str(e)}")
        raise


def create_stream(messages: List[Message]) -> Generator[ChatResponse, None, None]:
    prompt = [message.to_map() for message in messages]

    output = llm.create_chat_completion(
        prompt,
        stream=True,
        tools=tools_define.tools,
        tool_choice="auto",
    )  # type: ignore
    last_role = None
    for chunk in output:
        response, last_role = ChatResponse.from_stream_chunk(chunk, last_role)  # type: ignore
        if response.choices:
            yield response
