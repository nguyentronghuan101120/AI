from enum import Enum
import inspect
from pydantic import TypeAdapter

from services import image_service, stock_service, weather_service, web_data_service

class ToolFunction(Enum):
    GET_CURRENT_WEATHER = weather_service.fetch_weather_data.__name__
    GENERATE_IMAGE = image_service.generate_image_url.__name__
    READ_WEB_URL = web_data_service.read_web_url.__name__
    GET_STOCK_SYMBOL = stock_service.get_stock_symbol.__name__
    GET_STOCK_PRICE = stock_service.get_stock_price.__name__

def create_tool(function: callable) -> dict:
    """Creates a standardized tool dictionary."""
    return {
        "type": "function",
        "function": {
            "name": function.__name__,
            "description": inspect.getdoc(function),
            "parameters": TypeAdapter(function).json_schema(),
        },
        "strict": True
    }


# Tools definition
tools = [
    create_tool(
        function=image_service.generate_image_url,
    ),
    create_tool(
        function=weather_service.fetch_weather_data,
    ),
    create_tool(
        function=web_data_service.read_web_url,
    ),
    create_tool(
        function=stock_service.get_stock_symbol,
    ),
    create_tool(
        function=stock_service.get_stock_price,
    ),
]
