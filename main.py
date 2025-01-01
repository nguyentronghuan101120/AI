import os
from dotenv import load_dotenv
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

import client

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = openai.OpenAI(
    base_url="http://localhost:1234/v1",
    api_key='none',
)

chat_history = []

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_history

    messages = []

    for user_message, bot_message in chat_history:
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": bot_message})
    
    user_message = update.message.text
    messages.append({"role": "user", "content": user_message})

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="meta-llama/llama-3.2-3b-instruct",
    )

    bot_message = chat_completion.choices[0].message.content
    chat_history.append((user_message, bot_message))

    await context.bot.send_message(chat_id=update.message.chat_id, text=bot_message)

chat_handler = MessageHandler(filters=filters.TEXT & (~filters.COMMAND), callback=chat)

application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(chat_handler)

print("Bot is running...")
application.run_polling()