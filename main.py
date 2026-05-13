import os
import logging
from dotenv import load_dotenv
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Load environment variables from .env file
load_dotenv()

# Configuration from Environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-1.5-flash" # Consistent with current stable releases

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. Initialize Gemini Client
client = genai.Client(api_key=GOOGLE_API_KEY)

# 2. Refactored Response Logic
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes incoming Telegram messages and fetches AI responses."""
    user_text = update.message.text
    
    try:
        # Show 'typing' status in Telegram for better UX
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_text
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("The AI returned an empty response. Please try again.")
            
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        await update.message.reply_text("I'm experiencing a temporary connection issue. Please try again later.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not GOOGLE_API_KEY:
        logger.error("Missing API Keys! Ensure .env file is configured correctly.")
        exit(1)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logger.info("Bot is live and polling...")
    app.run_polling()