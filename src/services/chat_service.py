from constants import system_prompts
from models.requests.chat_request import ChatRequest
from services import vector_store_service

# from utils.llama_cpp_client import create, create_stream
from utils.clients import llama_cpp_client, transformer_client
from utils.timing import measure_time
from utils.tools import tools_helper


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
    tool_calls = []

    with measure_time("Generate stream"):
        stream = llama_cpp_client.generate_stream(messages=messages, has_tool_call=True)
        for chunk in stream:
            if chunk.get("choices", [])[0].get("delta", {}).get("tool_calls"):
                tool_calls.extend(
                    chunk.get("choices", [])[0].get("delta", {}).get("tool_calls")
                )
            else:
                yield chunk

    if not tool_calls:
        return

    with measure_time("Tool call handling"):
        tool_call_result = tools_helper.process_tool_calls(tool_calls)
        tool_call_message = {
            "role": "tool",
            "content": tool_call_result.get("content", ""),
        }
        messages.append(tool_call_message)

    with measure_time("Generate new stream"):
        new_stream = llama_cpp_client.generate_stream(messages, has_tool_call=False)
        for chunk in new_stream:
            yield chunk


def chat_generate(request: ChatRequest):
    """Non-streaming (batched) chat generation."""
    messages = build_context_prompt(request)
    messages.extend(request.messages)

    with measure_time("Generate chat completion"):
        output = llama_cpp_client.generate(messages=messages)

        choices = output.get("choices", [])

        tool_calls = choices[0].get("message").get("tool_calls")

        if not tool_calls:
            return output

    with measure_time("Tool call handling"):
        tool_call_result = tools_helper.process_tool_calls(tool_calls=tool_calls)
        tool_call_message = {
            "role": "tool",
            "content": tool_call_result.get("content", ""),
        }
        messages.append(tool_call_message)

    with measure_time("Generate new chat completion"):
        new_output = llama_cpp_client.generate(messages=messages, has_tool_call=False)

        return new_output
