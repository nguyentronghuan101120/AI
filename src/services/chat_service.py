from typing import AsyncGenerator
from models.requests.chat_request import ChatRequest
from utils import function_tools
from utils.client import openai_client


def chat_generate(request: ChatRequest):
    """
    Generate a complete chat response based on the given prompt.

    Args:
        request (ChatRequest): The chat request containing the prompt.

    Returns:
        str: The generated chat response as a string.
    """
    completion = openai_client.chat.completions.create(
        messages=request.prompt,
        model='',  # Specify the model name before using
        stream=False,
        tools=function_tools.tools  # Uncomment if tools are required
    )
    
    # Ensure choices exist before accessing message content
    return completion.choices[0].message


def chat_generate_stream(request: ChatRequest):
    """
    Generate a chat response in a streaming manner.

    Args:
        request (ChatRequest): The chat request containing the prompt.

    Returns:
        AsyncGenerator[str, None]: An asynchronous generator yielding response chunks.
    """
    # Streaming chat response in chunks
    stream = openai_client.chat.completions.create(
        messages=request.prompt,
        model='',  # Specify the model name before using
        stream=True,
        tools=function_tools.tools  # Uncomment if tools are required
    )
    
    return stream


async def get_model_info() -> dict:
    """
    Retrieve information about the currently loaded chat model.

    Returns:
        dict: A dictionary containing the model's name and version.
    """
    return {
        "model_name": "GPT-2",  # Update with actual model name if different
        "model_version": "1.0.0"
    }
