import json
from constants import system_prompts
from models.requests.chat_request import ChatRequest
from utils.tools import tools_helper
from utils.client import openai_client
from utils.tools import tools_define


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

def _build_conversation_history(message: str, chat_history: list) -> list:
    """Xây dựng lịch sử hội thoại theo định dạng yêu cầu."""
    messages = [{"role": "system", "content": system_prompts.system_prompt}]
    
    for user_message, bot_message in chat_history:
        if user_message:
            messages.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": bot_message}
            ])
    
    messages.append({"role": "user", "content": message})
    return messages


def _process_chat_stream(chat_stream, chat_history):
    """Xử lý luồng dữ liệu từ OpenAI API."""
    final_tool_calls = {}

    for chunk in chat_stream:
        delta = chunk.choices[0].delta
        
        if "TOOL_REQUEST" in chat_history[-1][1]:
            chat_history[-1][1] = "Please wait while I'm requesting a tool..."
            yield "", chat_history

        if getattr(delta, 'tool_calls', None):
            final_tool_calls = tools_helper.final_tool_calls_handler(final_tool_calls, delta.tool_calls)
            
        if delta.content:
            chat_history[-1][1] += delta.content
            yield "", chat_history

    return final_tool_calls


def _handle_tool_calls(final_tool_calls, messages, chat_history):
    """Xử lý kết quả của tool calls."""
    if not final_tool_calls:
        return

    tool_call_message = tools_helper.process_tool_calls(final_tool_calls)
    messages.append(tool_call_message)

    chat_stream = chat_generate_stream(ChatRequest(prompt=messages))
    for chunk in chat_stream:
        delta_content = chunk.choices[0].delta.content
        if delta_content:
            chat_history[-1][1] += delta_content
            yield "", chat_history

    tool_call_name = tool_call_message.get("tool_call_name")

    if tool_call_name == tools_define.ToolFunction.GENERATE_IMAGE.value:
        content = tool_call_message.get("content")
        chat_history.append([None, (content, '')])
        yield "", chat_history
        
    elif tool_call_name == tools_define.ToolFunction.GET_STOCK_SYMBOL.value:
        content = messages[-1]["content"]
        yield from chat_logic(content, chat_history)


def chat_logic(message: str, chat_history: list):
    """Hàm chính xử lý chat logic."""
    messages = _build_conversation_history(message, chat_history)

    chat_history.append([message, "Processing your request, please wait..."])
    yield "", chat_history

    chat_stream = chat_generate_stream(ChatRequest(prompt=messages, hasTool=True))
    chat_history[-1][1] = ""

    final_tool_calls = yield from _process_chat_stream(chat_stream, chat_history)
    yield from _handle_tool_calls(final_tool_calls, messages, chat_history)

    return "", chat_history
