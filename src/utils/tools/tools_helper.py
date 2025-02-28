import json
from utils.tools.tools_define import ToolFunction
from services import stock_service, weather_service, image_service, web_data_service

def extract_tool_args(tool_call):
    """
    Extract arguments from a tool call.
    
    Args:
        tool_call: The tool call object containing function arguments
        
    Returns:
        dict: The extracted arguments as a dictionary
    """
    return json.loads(tool_call.function.arguments)

def handle_weather_tool_call(tool_call):
    """
    Handle weather information tool call.
    
    Args:
        tool_call: The tool call object containing weather query parameters
        
    Returns:
        dict: Weather information including temperature, conditions etc.
    """
    args = extract_tool_args(tool_call)
    weather_info = weather_service.fetch_weather_data(args.get("latitude"), args.get("longitude"), args.get("unit"))
    return weather_info

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

def handle_stock_symbal_find_tool_call(tool_call):
    """
    Handle stock symbol find tool call.
    
    Args:
        tool_call: The tool call object containing company name
        
    Returns:
        dict: Stock information data
    """
    args = extract_tool_args(tool_call)
    stock_info = stock_service.get_stock_symbol(args.get("company"))
    return stock_info

def handle_stock_price_tool_call(tool_call):
    """
    Handle stock price information tool call.
    
    Args:
        tool_call: The tool call object containing stock symbol
        
    Returns:
        dict: Current stock price data
    """
    args = extract_tool_args(tool_call)
    stock_info = stock_service.get_stock_price(args.get("symbol"))
    return stock_info

def process_tool_calls(final_tool_calls):
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
        ToolFunction.GET_CURRENT_WEATHER.value: handle_weather_tool_call,
        ToolFunction.GENERATE_IMAGE.value: handle_image_tool_call,
        ToolFunction.READ_WEB_URL.value: handle_web_data_tool_call,
        ToolFunction.GET_STOCK_SYMBOL.value: handle_stock_symbal_find_tool_call,
        ToolFunction.GET_STOCK_PRICE.value: handle_stock_price_tool_call,
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
    """
    Handle and combine multiple tool calls.
    
    Args:
        final_tool_calls (dict): Existing tool calls dictionary
        tool_calls (list): New tool calls to process
        
    Returns:
        dict: Updated tool calls dictionary with combined arguments
    """
    for tool_call in tool_calls:
        index = tool_calls.index(tool_call)
        if index not in final_tool_calls:
            final_tool_calls[index] = tool_call
        
        final_tool_calls[index].function.arguments += tool_call.function.arguments
    
    return final_tool_calls
