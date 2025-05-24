from email import message

from flask import message_flashed
from constants import system_prompts
from models.requests.chat_request import ChatRequest
from models.responses.chat_response import ChatResponse
from services import vector_store_service

from utils.llama_cpp_client import create, create_stream
from utils.timing import measure_time
from utils.tools import tools_helper, tools_define
from models.others.message import Message, Role


def build_context_prompt(request: ChatRequest) -> list[Message]:
    """Build system prompt with context if file is provided."""
    messages = [Message(role=Role.system, content=system_prompts.system_prompt)]

    if not request.has_file or not vector_store_service.check_if_collection_exists(
        request.chat_session_id
    ):
        return messages

    with measure_time("Get data from vector store"):
        vectorstore = vector_store_service.get_vector_store(request.chat_session_id)
        query = request.messages[-1].content
        results = vectorstore.similarity_search(query=query or "", k=10)

    if not results:
        return messages

    with measure_time("Building context prompt"):
        context = ""
    for document in results:
        # print(f"Document:{document.page_content[:50]}, score:{score}\n\n")
        source = document.metadata.get("file_id", "Unknown File")
        context += f"Context from file: {source}\n\n{document.page_content}\n\n"

    embedded_prompt = (
        "Use the following CONTEXT to answer the QUESTION.\n"
        "If you don't know the answer or are unsure, just say that you don't know.\n"
        "If question is empty or nothing, please summarize the context.\n"
        "Use an unbiased and journalistic tone.\n\n"
        f"CONTEXT: {context}\nQUESTION: {query}"
    )

    messages.append(Message(role=Role.system, content=embedded_prompt))
    return messages


def chat_generate_stream(
    request: ChatRequest,
):
    """Streaming chat generation."""
    messages = build_context_prompt(request)
    messages.extend(request.messages)

    # stream = open_ai_client.chat.completions.create(
    #     messages=messages, model="my-model", stream=True, tools=tools_define.tools
    # )

    stream = create_stream(messages)

    final_tool_calls = {}

    for chunk in stream:
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if getattr(delta, "tool_calls", None):
                final_tool_calls = tools_helper.final_tool_calls_handler(
                    final_tool_calls, delta.tool_calls, is_stream=True
                )
            yield chunk

    if not final_tool_calls:
        return

    tool_call_result = tools_helper.process_tool_calls(final_tool_calls)
    tool_call_message = Message(
        role=Role.tool, content=tool_call_result.get("content", "")
    )
    messages.append(tool_call_message)

    new_stream = open_ai_client.chat.completions.create(
        messages=messages, model="my-model", stream=True
    )

    # new_stream = create_stream(messages)

    for chunk in new_stream:
        yield chunk


def chat_generate(request: ChatRequest):
    """Non-streaming (batched) chat generation."""
    messages = build_context_prompt(request)
    messages.extend(request.messages)

    # output = open_ai_client.chat.completions.create(
    #     messages=messages, model="my-model", tools=tools_define.tools
    # )
    output = create(messages=messages)

    final_tool_calls = {}

    message = None
    if output.choices and len(output.choices) > 0:
        message = output.choices[0].message
        if (
            message is not None
            and getattr(message, "tool_calls", None)
            and message.tool_calls
        ):
            final_tool_calls = tools_helper.final_tool_calls_handler(
                final_tool_calls=final_tool_calls, tool_calls=message.tool_calls
            )

    if not final_tool_calls:
        return output

    tool_call_result = tools_helper.process_tool_calls(
        final_tool_calls=final_tool_calls
    )
    tool_call_message = Message(
        role=Role.tool, content=tool_call_result.get("content", "")
    )
    messages.append(tool_call_message)

    new_output = create(messages=messages, has_tool_call=False)
    # new_output = open_ai_client.chat.completions.create(
    #     messages=messages, model="my-model", tools=tools_define.tools
    # )

    return new_output
