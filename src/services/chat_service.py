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
        tools=tools_define.tools if request.hasTool else None
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
        tools=tools_define.tools if request.hasTool else None
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
        request=ChatRequest(prompt=messages, hasTool=True)
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
            final_tool_calls = tools_helper.final_tool_calls_handler(final_tool_calls, delta.tool_calls)
     
    if final_tool_calls:
        chat_history[-1][1] = ""
        tool_call_message = tools_helper.process_tool_calls(final_tool_calls)
        
        messages.append(tool_call_message)
        
        final_response = chat_generate_stream(ChatRequest(prompt=messages, hasTool=False))
        for chunk in final_response:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                chat_history[-1][1] += delta_content
                yield "", chat_history
        
        tool_call_name = tool_call_message.get("tool_call_name")
        if tool_call_name == tools_define.ToolFunction.GENERATE_IMAGE.value:
            image_path = tool_call_message.get("content")
            chat_history.append([None, (image_path, '')])
            yield "", chat_history
                
    
    return "", chat_history
