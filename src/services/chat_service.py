from constants import system_prompts, tools_define
from models.requests.chat_request import ChatRequest
from utils import tools_helper
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
        tools=tools_define.tools  # Uncomment if tools are required
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
        tools=tools_define.tools
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

def chat_logic(message, chat_history):
    """Hàm chính xử lý chat logic."""
    
    # Build conversation history
    messages = [{"role": "system", "content": system_prompts.system_prompt}]
    
    for user_message, bot_message in chat_history:
        if user_message is not None:
            messages.append({"role": "user", "content": user_message})
            messages.append({"role": "assistant", "content": bot_message})
    
    # Append new user message
    messages.append({"role": "user", "content": message})
    chat_history.append([message, "Processing your request, please wait..."])
    yield "", chat_history

    # Call OpenAI API
    chat_stream = chat_generate_stream(
        request=ChatRequest(prompt=messages)
    )

    chat_history[-1][1] = ""
    final_tool_calls = {}

    for chunk in chat_stream:
        delta = chunk.choices[0].delta
        
        # Nếu có nội dung phản hồi từ AI
        if delta.content:
            chat_history[-1][1] += delta.content
            yield "", chat_history

        # Nếu AI yêu cầu gọi tool
        if "TOOL_REQUEST" in chat_history[-1][1]:
            chat_history.pop()
            chat_history.append([message, "Please wait while I'm requesting a tool..."])
            yield "", chat_history
        
        if getattr(delta, 'tool_calls', None):
            final_tool_calls = tools_helper.final_tool_calls_handler(final_tool_calls, delta)
     
    if final_tool_calls:
        yield from tools_helper.process_tool_calls(final_tool_calls, chat_history)
        
    return "", chat_history
