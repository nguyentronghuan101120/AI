import os
from typing import Generator, List
from constants.config import GGUF_FILE_NAME, GGUF_REPO_ID
from utils.timing import measure_time
from utils.tools import tools_define

_llm = None

def load():
    try:
        import llama_cpp
    except ImportError:
        raise ImportError("llama_cpp is not installed. Please install it using 'pip install llama-cpp-python'.")
    
    global _llm
    
    _llm = llama_cpp.Llama.from_pretrained(
        repo_id=GGUF_REPO_ID,
        filename=GGUF_FILE_NAME,
        n_threads=os.cpu_count(),
        n_gpu_layers=-1,
        n_ctx=4096,
        verbose=True,
        # messages_to_prompt=messages_to_prompt,
        # completion_to_prompt=completion_to_prompt,
    )   

def create(messages: List[dict], has_tool_call: bool = True):
    if _llm is None:
        raise ValueError("LLM is not loaded. Please call load() first.")
    

    tools = tools_define.tools if has_tool_call else None
    tool_choice = "auto" if has_tool_call else "none"

    print("Starting create chat completion")

    try:
        with measure_time("Starting create chat completion"):
            output = _llm.create_chat_completion(
                messages,
                tools=tools,  # type: ignore
                tool_choice=tool_choice,
            )  # type: ignore
            return output
    except Exception as e:
        print(f"Error in create chat completion: {str(e)}")
        raise


def create_stream(messages: List[dict]) -> Generator[dict, None, None]:
    if _llm is None:
        raise ValueError("LLM is not loaded. Please call load() first.")
    

    output = _llm.create_chat_completion(
        messages,
        stream=True,
        tools=tools_define.tools,  # type: ignore
        tool_choice="auto",
    )  # type: ignore
    last_role = None
    for chunk in output:
        response, last_role = ChatResponse.from_stream_chunk(chunk, last_role)  # type: ignore
        if response.choices:
            yield response
