from constants import system_prompts
from models.requests.chat_request import ChatRequest
from services import vector_store_service
from utils.tools import tools_helper, tools_define
from utils.client import openai_client


def build_context_prompt(request: ChatRequest) -> list:
    """Build system prompt with context if file is provided."""
    messages = [{"role": "system", "content": system_prompts.system_prompt}]
    
    if not request.hasFile or vector_store_service.check_if_collection_exists(request.chat_session_id):
        return messages
    

    vectorstore = vector_store_service.get_vector_store(request.chat_session_id)
    query = request.prompt[-1]["content"]
    results = vectorstore.similarity_search(query=query, k=5)

    if not results:
        return messages

    context = ''
    for document in results:
        source = document.metadata.get('file_id', 'Unknown File')
        context += f"Context from file: {source}\n\n{document.page_content}\n\n"

    embedded_prompt = (
        "Use the following CONTEXT to answer the QUESTION at the end.\n"
        "If you don't know the answer or are unsure, just say that you don't know.\n"
        "Use an unbiased and journalistic tone.\n\n"
        f"CONTEXT: {context}\nQUESTION: {query}"
    )

    messages.append({"role": "system", "content": embedded_prompt})
    return messages


def _handle_tool_calls_and_yield(stream, messages):
    """Yield response from initial stream and process tool calls if needed."""
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
        model='my-model',
        stream=True
    )

    for chunk in new_stream:
        yield chunk


def chat_generate_stream(request: ChatRequest,):
    """Streaming chat generation."""
    messages = build_context_prompt(request)
    messages.extend(request.prompt)

    stream = openai_client.chat.completions.create(
        messages=messages,
        model='my-model',
        stream=True,
        tools=tools_define.tools
    )

    yield from _handle_tool_calls_and_yield(stream, messages)


def chat_generate(request: ChatRequest,):
    """Non-streaming (batched) chat generation."""
    messages = build_context_prompt(request)
    messages.extend(request.prompt)

    response = openai_client.chat.completions.create(
        messages=messages,
        model='my-model',
        tools=tools_define.tools
    )

    return response
