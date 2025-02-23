import json
from constants.tools_define import ToolFunction
from services import weather_service, image_service, web_data_service

def extract_tool_args(tool_call):
    """Trích xuất đối số từ tool_call."""
    return json.loads(tool_call.function.arguments)

def handle_weather_tool_call(tool_call):
    """Xử lý tool lấy thông tin thời tiết."""
    args = extract_tool_args(tool_call)
    weather_info = weather_service.fetch_weather_data(args.get("latitude"), args.get("longitude"), args.get("unit"))
    return weather_info

def handle_web_data_tool_call(tool_call):
    """Xử lý tool lấy thông tin web."""
    args = extract_tool_args(tool_call)
    web_data = web_data_service.read_web_url(args.get("url"))
    return web_data
    
def handle_image_tool_call(tool_call):
    """Xử lý tool tạo ảnh."""
    args = extract_tool_args(tool_call)
    prompt = args.get("prompt")
        
    image_path = image_service.generate_image_url(prompt)
    return image_path

def process_tool_calls(final_tool_calls):
    """Xử lý tất cả các tool được gọi."""
    content = ""
    tool_handlers = {
        ToolFunction.GET_CURRENT_WEATHER.value: handle_weather_tool_call,
        ToolFunction.GENERATE_IMAGE.value: handle_image_tool_call,
        ToolFunction.READ_WEB_URL.value: handle_web_data_tool_call,
    }

    for tool_call in final_tool_calls.values():
        handler = tool_handlers.get(tool_call.function.name)
        if handler:
            result = handler(tool_call)
            if isinstance(result, list):
                content = json.dumps(result)  # Convert list to JSON string if needed
            else:
                content = str(result)  # Ensure content is a string

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "tool_call_name": tool_call.function.name,
        "content": content
    }

def process_tool_calls(final_tool_calls):
    """Xử lý tất cả các tool được gọi."""
    content = ""
    tool_handlers = {
        ToolFunction.GET_CURRENT_WEATHER.value: handle_weather_tool_call,
        ToolFunction.GENERATE_IMAGE.value: handle_image_tool_call,
        ToolFunction.READ_WEB_URL.value: handle_web_data_tool_call,
    }

    for tool_call in final_tool_calls.values():
        handler = tool_handlers.get(tool_call.function.name)
        if handler:
            result = handler(tool_call)
            if isinstance(result, list):
                content = json.dumps(result)  # Convert list to JSON string if needed
            else:
                content = str(result)  # Ensure content is a string

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "tool_call_name": tool_call.function.name,
        "content": content
    }

def final_tool_calls_handler(final_tool_calls, tool_calls):
    """Xử lý các tool được yêu cầu."""
    for tool_call in tool_calls:
        index = tool_calls.index(tool_call)
        if index not in final_tool_calls:
            final_tool_calls[index] = tool_call
        
        final_tool_calls[index].function.arguments += tool_call.function.arguments
    
    return final_tool_calls
