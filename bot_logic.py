import os
import logging
import pythonbible as bible
from groq import Groq
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MODEL_NAME = "llama-3.3-70b-versatile"

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)
user_conversations = {}

def fetch_scripture(query):
    """Encapsulated logic for bible library interaction."""
    try:
        references = bible.get_references(query)
        if not references: 
            return None
            
        verse_ids = bible.convert_reference_to_verse_ids(references[0])
        text = "".join([f"<i>{bible.get_verse_text(v_id).strip()}</i>\n\n" for v_id in verse_ids])
        title = bible.format_scripture_references(references)
        
        return f"📖 <b>{title} (KJV)</b>\n\n{text}"
    except Exception as e:
        logger.error(f"Bible Library Error: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id 
    user_text = update.message.text
    if not user_text: 
        return

    # Initialize session with System Prompt
    if chat_id not in user_conversations:
        user_conversations[chat_id] = [
            {
                "role": "system", 
                "content": "You are a wise Bible study assistant. Use HTML tags: <b>bold</b>, <i>italic</i>. Use bullets (•). Keep paragraphs clean."
            }
        ]

    # 1. Check for Scripture First
    scripture = fetch_scripture(user_text)
    
    if scripture:
        user_conversations[chat_id].append({"role": "assistant", "content": f"Shared: {scripture}"})
        try:
            await update.message.reply_text(scripture, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Failed sending scripture with HTML parse mode: {e}")
            await update.message.reply_text(scripture) # Fallback to plain text response
        return

    # 2. Proceed to AI Chat if no scripture found
    user_conversations[chat_id].append({"role": "user", "content": user_text})
    
    # Maintain sliding window context (memory management)
    if len(user_conversations[chat_id]) > 12:
        user_conversations[chat_id] = [user_conversations[chat_id][0]] + user_conversations[chat_id][-11:]

    # Define fallback response explicitly before the AI completion blocks
    fallback_response = "Sorry, I am having trouble connecting to my brain right now. Please try again."

    try:
        # Show "typing" indicator to user
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        chat_completion = client.chat.completions.create(
            messages=user_conversations[chat_id],
            model=MODEL_NAME,
            temperature=0.7,
        )
        
        ai_response = chat_completion.choices[0].message.content
        user_conversations[chat_id].append({"role": "assistant", "content": ai_response})
        
        await update.message.reply_text(ai_response, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Chat Completion/Formatting Error: {e}")
        # Safely fallback to plain text using local scoped fallback string
        await update.message.reply_text(fallback_response)

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        logger.error("No Telegram Token found!")
        exit(1)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logger.info(" Stable Bible Assistant is ONLINE.")
    app.run_polling()
