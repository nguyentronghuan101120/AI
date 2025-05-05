import json
import base64
import os
from constants import system_prompts
from models.requests.chat_request import ChatRequest
from services.process_file_service import get_file_content, get_vector_store
from utils.tools import tools_helper
from utils.client import openai_client
from utils.tools import tools_define

def chat_generate_stream(request: ChatRequest):
    """
    Generate a chat response in a streaming manner.

    Args:
        request (ChatRequest): The chat request containing the prompt and optional file content.

    Returns:
        AsyncGenerator[str, None]: An asynchronous generator yielding response chunks.
    """
    
    messages = [{"role": "system", "content": system_prompts.system_prompt}]
    
    if(request.file is not None):
        vectorstore = get_vector_store(request.file.file_id)
        results = vectorstore.similarity_search(query=request.prompt[-1]["content"], k=3)
        
        context = ''
        
        for document in results:
            context += document.page_content + "\n\n"
        
        embedded_system_prompt = f"""
        Use the following CONTEXT to answer the QUESTION at the end.
        If you don't know the answer or unsure of the answer, just say that you don't know, don't try to make up an answer.
        Use an unbiased and journalistic tone.

        CONTEXT: {context}
        QUESTION: {request.prompt}
        """
        
        messages.append({"role": "system", "content": embedded_system_prompt})
        
        
    messages.extend(request.prompt)
        
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