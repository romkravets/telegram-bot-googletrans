import os
import sys
import logging
from dotenv import load_dotenv
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DB_PATH = os.getenv("DB_PATH", "./data/translate_bot.db")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

if not DEEPL_API_KEY:
    logging.warning("DEEPL_API_KEY not set — using Google Translate only")

from db.storage import init_db
from handlers.start import start_command, lang_command, help_command, language_callback
from handlers.translate import translate_text_handler, forwarded_message_handler
from handlers.photo import photo_handler


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN not set in .env")

    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    init_db(DB_PATH)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang:"))

    # FORWARDED must be before TEXT: a forwarded text message matches both filters,
    # and the first registered handler in the same group wins
    app.add_handler(MessageHandler(filters.FORWARDED, forwarded_message_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    logging.info("Bot started. Polling...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
