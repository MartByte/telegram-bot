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

# --- KEYS ---
GROQ_API_KEY = "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"
TELEGRAM_TOKEN = "6102433125:AAGslqmuK7aaxbA7jfS6Vp1chKHdVkWRbR8"

client = Groq(api_key=GROQ_API_KEY)

# This dictionary will store the last 5 messages for each user
# Format: {user_id: [messages]}
user_conversations = {}

def fetch_scripture(query):
    try:
        references = bible.get_references(query)
        if not references: return None
        verse_ids = bible.convert_reference_to_verse_ids(references[0])
        text = "".join([f"{bible.get_verse_text(v_id)}\n" for v_id in verse_ids])
        title = bible.format_scripture_references(references)
        return f"📖 **{title} (KJV)**\n\n{text}"
    except: return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    if not user_text: return

    # Initialize memory for new users
    if user_id not in user_conversations:
        user_conversations[user_id] = [
            {"role": "system", "content": "You are a wise Bible study assistant. Remember the context of the conversation."}
        ]

    scripture = fetch_scripture(user_text)
    
    if scripture:
        # If it's a verse, we add it to the memory so the AI knows we just read it
        user_conversations[user_id].append({"role": "assistant", "content": f"Shared scripture: {scripture}"})
        await update.message.reply_text(scripture, parse_mode='Markdown')
    else:
        # Add user's question to memory
        user_conversations[user_id].append({"role": "user", "content": user_text})
        
        # Keep only the last 10 messages to save "tokens" (memory space)
        if len(user_conversations[user_id]) > 10:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-9:]

        try:
            chat_completion = client.chat.completions.create(
                messages=user_conversations[user_id], # Send the WHOLE history
                model="llama-3.3-70b-versatile",
            )
            
            ai_response = chat_completion.choices[0].message.content
            
            # Add AI's response to memory too!
            user_conversations[user_id].append({"role": "assistant", "content": ai_response})
            
            await update.message.reply_text(ai_response)
        except Exception as e:
            await update.message.reply_text("I lost my train of thought. Try again?")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("⚡ Memory-Enabled Bible Bot is ONLINE.")
    app.run_polling()