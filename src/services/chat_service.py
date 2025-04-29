import json
from constants import system_prompts
from models.requests.chat_request import ChatRequest
from utils.tools import tools_helper
from utils.client import openai_client
from utils.tools import tools_define

def chat_generate_stream(request: ChatRequest):
    """
    Generate a chat response in a streaming manner.

    Args:
        request (ChatRequest): The chat request containing the prompt.

    Returns:
        AsyncGenerator[str, None]: An asynchronous generator yielding response chunks.
    """
    
    # Add system prompt to the beginning of messages
    messages = [{"role": "system", "content": system_prompts.system_prompt}] + request.prompt
    
    # Streaming chat response in chunks
    stream = openai_client.chat.completions.create(
        messages=messages,
        model='', 
        stream=True,
        tools=tools_define.tools if request.hasTool else None
    )
    
    final_tool_calls = {}
    
    for chunk in stream:
        delta = chunk.choices[0].delta
        if getattr(delta, 'tool_calls', None):
            final_tool_calls = tools_helper.final_tool_calls_handler(final_tool_calls, delta.tool_calls)
        yield chunk
        
    if not final_tool_calls:
        return

    tool_call_message = tools_helper.process_tool_calls(final_tool_calls)
    
    messages.append(tool_call_message)
    
    new_stream = openai_client.chat.completions.create(
        messages=messages,
        model='', 
        stream=True,
    )
    
    for chunk in new_stream:
        yield chunk
