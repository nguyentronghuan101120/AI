import json
from constants.tools_define import ToolFunction
from services import weather_service, image_service

def extract_tool_args(tool_call):
    """Trích xuất đối số từ tool_call."""
    return json.loads(tool_call.function.arguments)

def handle_weather_tool_call(tool_call, chat_history):
    """Xử lý tool lấy thông tin thời tiết."""
    args = extract_tool_args(tool_call)
    weather = weather_service.get_weather(args.get("location"), args.get("unit"))
    chat_history.append([None, weather])
    return chat_history
    
def handle_image_tool_call(tool_call, chat_history):
    """Xử lý tool tạo ảnh."""
    args = extract_tool_args(tool_call)
    prompt = args.get("prompt")
    
    chat_history.append([None, "Please wait while I'm generating the image..."])
    yield "", chat_history
    
    image_path = image_service.generate_image_url(prompt)
    chat_history.append([None, "This is the image I've created for you, please enjoy it!"])
    chat_history.append([None, (image_path, prompt)])
    
    return chat_history

def process_tool_calls(final_tool_calls, chat_history):
    """Xử lý tất cả các tool được gọi."""
    tool_handlers = {
        ToolFunction.GET_CURRENT_WEATHER.value: handle_weather_tool_call,
        ToolFunction.GENERATE_IMAGE.value: handle_image_tool_call,
    }

    for tool_call in final_tool_calls.values():
        chat_history[-1][1] = ""  
        handler = tool_handlers.get(tool_call.function.name)
        if handler:
            chat_history = handler(tool_call, chat_history)
        yield "", chat_history

def final_tool_calls_handler(final_tool_calls, delta):
    """Xử lý các tool được yêu cầu."""

    if getattr(delta, 'tool_calls', None):
        tool_calls = delta.tool_calls
        for tool_call in tool_calls:
            index = tool_calls.index(tool_call)
            if index not in final_tool_calls:
                final_tool_calls[index] = tool_call
            
            final_tool_calls[index].function.arguments += tool_call.function.arguments
    
    return final_tool_calls
