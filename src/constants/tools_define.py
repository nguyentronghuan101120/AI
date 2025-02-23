from enum import Enum


class ToolFunction(Enum):
    GET_CURRENT_WEATHER = "get_current_weather"
    GENERATE_IMAGE = "generate_image"


def create_tool(name: ToolFunction, description: str, properties: dict, required=None, strict=False) -> dict:
    """Creates a standardized tool dictionary."""
    return {
        "type": "function",
        "function": {
            "name": name.value,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                **({"required": required} if required else {}),
            },
        },
        **({"strict": True} if strict else {}),
    }


# Define tool properties separately for better maintainability
IMAGE_TOOL_PROPERTIES = {
    "prompt": {
        "type": "string",
        "description": "The prompt used for generating the image (must be in English)",
    }
}

WEATHER_TOOL_PROPERTIES = {
    "location": {"type": "string", "description": "The city name"},
    "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "The temperature unit",
    },
}

# Tools definition
tools = [
    create_tool(
        name=ToolFunction.GENERATE_IMAGE,
        description="Creates an image based on the specified prompt using DiffusionPipeline",
        properties=IMAGE_TOOL_PROPERTIES,
    ),
    create_tool(
        name=ToolFunction.GET_CURRENT_WEATHER,
        description="Get the current weather in a given location",
        properties=WEATHER_TOOL_PROPERTIES,
        required=["location", "unit"],
    ),
]
