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

# llm = llama_cpp.Llama(
#     model_path=FILE_NAME,
#     n_threads=n_threads,
#     n_gpu_layers=n_gpu_layers,
#     n_ctx=4096,
#     # chat_format="chatml_function_calling",  # <-- important for tool/function calling
#     verbose=False,
# )

llm = llama_cpp.Llama.from_pretrained(
    repo_id=REPO_ID,
    filename=FILE_NAME,
    n_threads=os.cpu_count(),
    n_gpu_layers=-1,
    n_ctx=4096,
    verbose=True,
)

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
