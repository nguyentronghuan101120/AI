from enum import Enum
import inspect
from pydantic import TypeAdapter

from services import image_service, web_data_service

class ToolFunction(Enum):
    GENERATE_IMAGE = image_service.generate_image_url.__name__
    READ_WEB_URL = web_data_service.read_web_url.__name__
    SEARCH_WEB = web_data_service.search_web.__name__

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
        function=web_data_service.read_web_url,
    ),
    create_tool(
        function=web_data_service.search_web,
    ),
]
