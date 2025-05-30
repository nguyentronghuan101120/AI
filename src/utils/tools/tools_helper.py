import json
import re
from typing import List
import uuid
from utils.tools.tools_define import ToolFunction
from services import image_service, web_data_service


def extract_tool_args(tool_call):
    """
    Extract arguments from a tool call.

    Args:
        tool_call: The tool call object containing function arguments

    Returns:
        dict: The extracted arguments as a dictionary
    """
    return tool_call.get("function", {}).get("arguments", "{}")


def handle_web_data_tool_call(tool_call):
    """
    Handle web data extraction tool call.

    Args:
        tool_call: The tool call object containing URL to read

    Returns:
        str: The extracted web page content
    """
    args = extract_tool_args(tool_call)
    web_data = web_data_service.read_web_url(args.get("url"))
    return web_data


def handle_image_tool_call(tool_call):
    """
    Handle image generation tool call.

    Args:
        tool_call: The tool call object containing image generation prompt

    Returns:
        str: Path to the generated image
    """
    args = extract_tool_args(tool_call)
    prompt = args.get("prompt")

    image_path = image_service.generate_image_url(prompt)
    return image_path


def handle_search_web_tool_call(tool_call):
    """
    Handle web search tool call.

    Args:
        tool_call: The tool call object containing search query

    Returns:
        str: The search results
    """
    args = extract_tool_args(tool_call)
    search_query = args.get("search_query")
    search_results = web_data_service.web_search_with_3rd_party(search_query)
    return search_results


def process_tool_calls(tool_calls):
    """
    Process all tool calls and execute them.

    Args:
        final_tool_calls (dict): Dictionary of tool calls to process

    Returns:
        dict: Result containing tool call response with:
            - role: The role of the response
            - tool_call_id: ID of the tool call
            - tool_call_name: Name of the called tool
            - content: Response content from the tool
    """
    content = ""
    tool_handlers = {
        ToolFunction.GENERATE_IMAGE.value: handle_image_tool_call,
        ToolFunction.READ_WEB_URL.value: handle_web_data_tool_call,
        ToolFunction.SEARCH_WEB.value: handle_search_web_tool_call,
    }

    for tool_call in tool_calls:
        handler = tool_handlers.get(tool_call.get("function").get("name"))
        if handler:
            result = handler(tool_call)
            if isinstance(result, list):
                content = json.dumps(result)  # Convert list to JSON string if needed
            else:
                content = str(result)  # Ensure content is a string

    return {
        "role": "tool",
        "tool_call_id": tool_call.get("id"),
        "tool_call_name": tool_call.get("function", {}).get("name"),
        "content": content,
    }


def extract_tool_calls_and_reupdate_output(text: str):
    """
    Extracts all valid JSON objects found within <tool_call>{...}</tool_call> patterns.
    Removes newlines and returns cleaned text and tool calls.
    """
    if text is None:
        return "", []
    
    tool_calls = []

    # Match any <tool_call> JSON-like structure (greedy to match full JSON block)
    pattern = r"<tool_call>\s*(\{.*?\})\s*</?tool_call>?"

    matches = list(re.finditer(pattern, text, re.DOTALL))

    for match in matches:
        try:
            tool_call = {}
            tool_call["id"] = str(uuid.uuid4())
            tool_call["type"] = "function"
            json_content = json.loads(match.group(1))
            tool_call["function"] = {
                "name": json_content.get("name", ""),
                "arguments": json_content.get("arguments", {}),
            }
            tool_calls.append(tool_call)
        except json.JSONDecodeError:
            continue


    # Remove tool calls from text and clean up
    text = re.sub(pattern, "", text, flags=re.DOTALL).strip()
    return text.strip(), tool_calls if tool_calls else None
