# import subprocess
# import sys
# import logging

# # --- AUTOMATIC LIBRARY CHECKER ---
# # This block checks for 'google-genai' and installs it if missing or outdated.
# def sync_libraries():
#     print("Checking for newest Google AI libraries...")
#     try:
#         # We try to install/upgrade the specific 2026 library
#         subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-genai", "python-telegram-bot"])
#         print("Libraries are up to date.")
#     except Exception as e:
#         print(f"Could not update libraries automatically: {e}")

# sync_libraries()
# # ---------------------------------

# from google import genai
# from telegram import Update
# from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# # 1. Setup the 2026 Gemini Client
# # Replace with your actual API key from Google AI Studio
# client = genai.Client(api_key="AIzaSyAQB5ZJmTn-xYVa-2ESgkreGk9V0K8Afxc")

# # 2. Setup Logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# # 3. Response Logic
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_text = update.message.text
    
#     try:
#         # Using the current 2026 stable free-tier model
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",  # 1.5-flash is currently the most reliable for Free Tier
#             contents=user_text
#         )
        
#         if response.text:
#             await update.message.reply_text(response.text)
#         else:
#             await update.message.reply_text("I understood you, but I couldn't generate a text response.")
            
#     except Exception as e:
#         print(f"--- DETAILED ERROR ---")
#         print(e) # This will tell you if it's still a 'limit: 0' issue
#         await update.message.reply_text("My quota is currently 0. I need to be activated in AI Studio!")
# if __name__ == '__main__':
#     # Replace with your actual Token from @BotFather
#     token = '6102433125:AAGslqmuK7aaxbA7jfS6Vp1chKHdVkWRbR8'
    
#     app = ApplicationBuilder().token(token).build()
#     app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
#     print("Bot is live! Talk to it on Telegram.")
#     app.run_polling()

import pythonbible as bible
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- YOUR PRIVATE KEYS ---
GROQ_API_KEY = "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"
TELEGRAM_TOKEN = "6102433125:AAGslqmuK7aaxbA7jfS6Vp1chKHdVkWRbR8"

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# Memory dictionary keyed by chat_id (The 'Shared Brain' for your channel)
user_conversations = {}

def fetch_scripture(query):
    """Detects Bible references and returns King James Version text."""
    try:
        references = bible.get_references(query)
        if not references:
            return None
        
        # Convert first reference found to verse text
        verse_ids = bible.convert_reference_to_verse_ids(references[0])
        text = "".join([f"{bible.get_verse_text(v_id)}\n" for v_id in verse_ids])
        
        title = bible.format_scripture_references(references)
        return f"📖 **{title} (KJV)**\n\n{text}"
    except Exception as e:
        print(f"Bible Library Error: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Using chat_id ensures the bot shares memory with everyone in the same channel
    chat_id = update.effective_chat.id 
    user_text = update.message.text
    if not user_text: 
        return

    # Initialize shared memory for this specific channel/chat if it doesn't exist
    if chat_id not in user_conversations:
        user_conversations[chat_id] = [
            {
                "role": "system", 
                "content": (
                    "You are a wise and encouraging Bible study assistant helping a group of friends. "
                    "Use the context of the entire conversation to provide helpful insights."
                )
            }
        ]

    # 1. Try to fetch literal Scripture first
    scripture = fetch_scripture(user_text)
    
    if scripture:
        # We manually add the scripture to the history so the AI 'knows' what was just read
        user_conversations[chat_id].append({"role": "assistant", "content": f"Shared scripture: {scripture}"})
        await update.message.reply_text(scripture, parse_mode='Markdown')
    else:
        # 2. Add the user's message to the SHARED history
        user_conversations[chat_id].append({"role": "user", "content": user_text})
        
        # Keep only the last 12 messages for better context and token management
        if len(user_conversations[chat_id]) > 12:
            # Keep the system instructions (index 0) and the last 11 messages
            user_conversations[chat_id] = [user_conversations[chat_id][0]] + user_conversations[chat_id][-11:]

        try:
            # Send the entire shared history to Groq
            chat_completion = client.chat.completions.create(
                messages=user_conversations[chat_id],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
            )
            
            ai_response = chat_completion.choices[0].message.content
            
            # Save the AI response into the shared memory too
            user_conversations[chat_id].append({"role": "assistant", "content": ai_response})
            
            await update.message.reply_text(ai_response)
            
        except Exception as e:
            print(f"Groq API Error: {e}")
            await update.message.reply_text("I'm reflecting on that... (The connection is a bit slow).")

if __name__ == '__main__':
    # Initialize the Telegram Application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Catch all text messages in the channel/chat
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("⚡ Shared-Memory Bible Bot is now ONLINE and running on Groq.")
    app.run_polling()