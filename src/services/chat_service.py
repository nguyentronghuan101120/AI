from constants import system_prompts
from models.requests.chat_request import ChatRequest
from services import vector_store_service

# from utils.llama_cpp_client import create, create_stream
from utils import open_ai_client
from utils.timing import measure_time
from utils.tools import tools_helper, tools_define
from utils.transformer_client import generate, generate_stream


def build_context_prompt(request: ChatRequest) -> list[dict]:
    """Build system prompt with context if file is provided."""
    messages = [{"role": "system", "content": system_prompts.system_prompt}]

    if not request.has_file or not vector_store_service.check_if_collection_exists(
        request.chat_session_id
    ):
        return messages

    with measure_time("Get data from vector store"):
        vectorstore = vector_store_service.get_vector_store(request.chat_session_id)
        query = request.messages[-1].get("content")
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

    messages.append({"role": "system", "content": embedded_prompt})
    return messages


def chat_generate_stream(
    request: ChatRequest,
):
    """Streaming chat generation."""
    messages = build_context_prompt(request)
    messages.extend(request.messages)

    # stream = generate_stream(messages)
    stream = open_ai_client.generate_stream(messages=messages, has_tool_call=True)
    
    tool_calls = []

    for chunk in stream:
        choices = chunk.get("choices", [])
        if choices and choices[0].get("delta", {}).get("tool_calls"):
            delta = choices[0]["delta"]
            tool_calls.extend(delta["tool_calls"])
        yield chunk

    if not tool_calls:
        return

    tool_call_result = tools_helper.process_tool_calls(tool_calls)
    tool_call_message = {"role": "tool", "content": tool_call_result.get("content", "")}
    messages.append(tool_call_message)


    # new_stream = generate_stream(messages)
    new_stream = open_ai_client.generate_stream(messages=messages, has_tool_call=False)
    for chunk in new_stream:
        yield chunk


def chat_generate(request: ChatRequest):
    """Non-streaming (batched) chat generation."""
    messages = build_context_prompt(request)
    messages.extend(request.messages)

    output = open_ai_client.generate(messages=messages)
    choices = output.get("choices", [])

    tool_calls = choices[0].get("message").get("tool_calls")

    if not tool_calls:
        return output

    tool_call_result = tools_helper.process_tool_calls(
        tool_calls=tool_calls
    )
    tool_call_message = {"role": "tool", "content": tool_call_result.get("content", "")}
    messages.append(tool_call_message)

    # new_output = generate(messages=messages, has_tool_call=False)
    new_output = open_ai_client.generate(messages=messages, has_tool_call=False)
    return new_output
