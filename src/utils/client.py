import os
from typing import Generator, List
import openai
import torch

from constants.config import FILE_NAME
from models.others.message import Message
from models.requests.chat_request import ChatRequest
from models.responses.chat_response import ChatResponse
from utils.tools import tools_define

# Initialize OpenAI API client
openai_client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="none",
)

from llama_cpp import ChatCompletionTool, Llama

# Determine number of CPU threads based on device
if torch.cuda.is_available() or (
    hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
):
    n_threads = 4  # Fewer threads if using GPU/MPS, adjust as needed
    n_gpu_layers = 20
else:
    n_threads = os.cpu_count() or 4
    n_gpu_layers = 0

# Khởi tạo mô hình từ GGUF
llm = Llama(
    model_path=FILE_NAME,
    n_threads=n_threads,
    n_gpu_layers=n_gpu_layers,
    n_ctx=4096,
)

def create(messages: List[Message]):
    prompt = [message.to_map() for message in messages]
    output = llm.create_chat_completion(prompt)  # type: ignore
    return output

def create_stream(messages: List[Message]) -> Generator[ChatResponse, None, None]:
    prompt = [message.to_map() for message in messages]
    output = llm.create_chat_completion(prompt, stream=True, tools=tools_define.tools)  # type: ignore
    last_role = None
    for chunk in output:
        response, last_role = ChatResponse.from_stream_chunk(chunk, last_role)  # type: ignore
        if response.choices:
            yield response
