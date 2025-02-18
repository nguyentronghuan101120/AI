import gradio as gr

from services.chat_service import chat_logic

try:
    with gr.Blocks() as demo:
        gr.Markdown("# My smart AI chatbot")
        message = gr.Textbox(label="Enter your message:")
        chatbot = gr.Chatbot(label="My smart AI chatbot", height=600)
        message.submit(chat_logic, [message, chatbot], [message, chatbot])

    demo.launch(share=True, allowed_paths=["../outputs"])
except Exception as e:
    print(f"Error initializing Gradio interface: {e}")
