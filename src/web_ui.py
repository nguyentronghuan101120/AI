import gradio as gr
import json

from models.requests.chat_request import ChatRequest
from services import chat_service, image_service, weather_service
from utils.prompts import system_prompt

def chat_logic(message, chat_history):
    # Build the conversation messages with the system prompt for context.
    messages = [{"role": "system", "content": system_prompt}]
    
    for user_message, bot_message in chat_history:
        if user_message is not None:
            messages.append({"role": "user", "content": user_message})
            messages.append({"role": "assistant", "content": bot_message})
    
    # Append the new user message.
    messages.append({"role": "user", "content": message})
    chat_history.append([message, "Processing your request, please wait..."])
    yield "", chat_history

    # Call the OpenAI API.
    chat_stream = chat_service.chat_generate_stream(
        request=ChatRequest(prompt=messages)
    )

    chat_history[-1][1] = ""
    final_tool_calls = {}

    for chunk in chat_stream:
        delta = chunk.choices[0].delta
        
        if delta.content:
            chat_history[-1][1] += delta.content
            yield "", chat_history

        if isinstance(chat_history[-1][1], str) and "TOOL_REQUEST" in chat_history[-1][1]:
            chat_history.pop()
            chat_history.append([message, "Please wait while I'm request a tool..."])
            yield "", chat_history

        if getattr(delta, 'tool_calls', None):
            tool_calls = delta.tool_calls
            for tool_call in tool_calls:
                index = tool_calls.index(tool_call)
                if index not in final_tool_calls:
                    final_tool_calls[index] = tool_call
                
                final_tool_calls[index].function.arguments += tool_call.function.arguments

    if final_tool_calls:
        for index, tool_call in final_tool_calls.items():
            chat_history[-1][1] = "" 
            if tool_call.function.name == "get_current_weather":
                function_arguments = json.loads(tool_call.function.arguments)
                location = function_arguments.get("location")
                unit = function_arguments.get("unit")
                weather = weather_service.get_weather(location, unit)
                chat_history.append([None, weather])
            elif tool_call.function.name == "generate_image":
                function_arguments = json.loads(tool_call.function.arguments)
                prompt = function_arguments.get("prompt")
                chat_history.append([None, "Please wait while I'm generating the image..."])
                yield "", chat_history
                image_path = image_service.generate_image_url(prompt)
                chat_history[-1][1] = "" 
                chat_history.append([None, "This is the image I've created for you, please enjoy it!"])
                chat_history.append([None, (image_path, prompt)])
            yield "", chat_history

    return "", chat_history

try:
    with gr.Blocks() as demo:
        gr.Markdown("# My smart AI chatbot")
        message = gr.Textbox(label="Enter your message:")
        chatbot = gr.Chatbot(label="My smart AI chatbot", height=600)
        message.submit(chat_logic, [message, chatbot], [message, chatbot])

    demo.launch(share=True, allowed_paths=["../outputs"])
except Exception as e:
    print(f"Error initializing Gradio interface: {e}")
