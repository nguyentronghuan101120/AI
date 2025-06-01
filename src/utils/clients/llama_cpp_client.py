import os
from typing import Generator, List
import uuid
from constants.config import GGUF_FILE_NAME, GGUF_REPO_ID
from utils.stream_helper import process_stream_content
from utils.timing import measure_time
from utils.tools import tools_define
from utils.tools.tools_helper import extract_tool_calls_and_reupdate_output

_llm = None


def load():
    try:
        import llama_cpp
    except ImportError:
        raise ImportError(
            "llama_cpp is not installed. Please install it using 'pip install llama-cpp-python'."
        )

    global _llm

    _llm = llama_cpp.Llama.from_pretrained(
        repo_id=GGUF_REPO_ID,
        filename=GGUF_FILE_NAME,
        n_threads=os.cpu_count(),
        n_gpu_layers=-1,
        n_ctx=4096,
        verbose=True,
        use_mlock=True,
        use_mmap=True,
        # messages_to_prompt=messages_to_prompt,
        # completion_to_prompt=completion_to_prompt,
    )


def generate(messages: List[dict], has_tool_call: bool = True):
    if _llm is None:
        raise ValueError("LLM is not loaded. Please call load() first.")

    tools = tools_define.tools if has_tool_call else None
    tool_choice = "auto" if has_tool_call else "none"

    try:
        output = _llm.create_chat_completion(
            messages,  # type: ignore
            tools=tools,  # type: ignore
            tool_choice=tool_choice,
        )

        cleaned_output, tool_calls = extract_tool_calls_and_reupdate_output(
            output.get("choices", [])[0].get("message", {}).get("content", "")  # type: ignore
        )

        return {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": cleaned_output,
                        "tool_calls": tool_calls,
                    },
                }
            ],
        }

    except Exception as e:
        print(f"Error in create chat completion: {str(e)}")
        raise


def generate_stream(
    messages: List[dict], has_tool_call: bool = True
) -> Generator[dict, None, None]:
    if _llm is None:
        raise ValueError("LLM is not loaded. Please call load() first.")

    tools = tools_define.tools if has_tool_call else None
    tool_choice = "auto" if has_tool_call else "none"

    output = _llm.create_chat_completion(
        messages,  # type: ignore
        stream=True,
        tools=tools_define.tools,  # type: ignore
        tool_choice="auto",
    )  # type: ignore

    def content_generator():
        for chunk in output:
            yield chunk.get("choices", [])[0].get("delta", {}).get("content", "")  # type: ignore

    yield from process_stream_content(content_generator())  # type: ignore
