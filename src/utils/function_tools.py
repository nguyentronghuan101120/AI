def create_tool(name, description, properties, required=None, strict=False):
    tool = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
            },
        },
    }
    if required:
        tool["function"]["parameters"]["required"] = required
    if strict:
        tool["strict"] = True
    return tool


tools = [
    create_tool(
        name="generate_image",
        description="Creates an image based on the specified prompt using DiffusionPipeline",
        properties={
            "prompt": {
                "type": "string",
                "description": "The prompt used for generating the image (must be in English)",
            },
        },
    ),
    create_tool(
        name="get_current_weather",
        description="Get the current weather in a given location",
        properties={
            "location": {"type": "string", "description": "The city name"},
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The temperature unit",
            },
        },
        required=["location", "unit"],
        strict=True,
    ),
]
