import subprocess
import sys
import logging

# --- AUTOMATIC LIBRARY CHECKER ---
# This block checks for 'google-genai' and installs it if missing or outdated.
def sync_libraries():
    print("Checking for newest Google AI libraries...")
    try:
        # We try to install/upgrade the specific 2026 library
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-genai", "python-telegram-bot"])
        print("Libraries are up to date.")
    except Exception as e:
        print(f"Could not update libraries automatically: {e}")

sync_libraries()
# ---------------------------------

from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. Setup the 2026 Gemini Client
# Replace with your actual API key from Google AI Studio
client = genai.Client(api_key="AIzaSyCdvU3xDJFxIbpAG_fhilSaxl-hIsoyRxI")

# 2. Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 3. Response Logic
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        # Using the current 2026 stable free-tier model
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # 1.5-flash is currently the most reliable for Free Tier
            contents=user_text
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("I understood you, but I couldn't generate a text response.")
            
    except Exception as e:
        print(f"--- DETAILED ERROR ---")
        print(e) # This will tell you if it's still a 'limit: 0' issue
        await update.message.reply_text("My quota is currently 0. I need to be activated in AI Studio!")
if __name__ == '__main__':
    # Replace with your actual Token from @BotFather
    token = '6102433125:AAGslqmuK7aaxbA7jfS6Vp1chKHdVkWRbR8'
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is live! Talk to it on Telegram.")
    app.run_polling()