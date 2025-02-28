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


# import gradio as gr

# from services.chat_service import chat_logic

# try:
#     with gr.Blocks() as demo:
#         chatbot = gr.Chatbot()

#         chat_input = gr.MultimodalTextbox(
#             interactive=True,
#             file_count="multiple",
#             placeholder="Enter message or upload file...",
#             show_label=False,
#             sources=["microphone", "upload"],
#         )

#         chat_msg = chat_input.submit(
#             chat_logic, [chatbot, chat_input], [chatbot, chat_input]
#         )
#         bot_msg = chat_msg.then(chat_logic, chatbot, chatbot, api_name="bot_response")
#         bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

#         chatbot.like(None, None, None, like_user_message=True)

#         demo.launch(share=True, allowed_paths=["../outputs"])
# except Exception as e:
#     print(f"Error initializing Gradio interface: {e}")
