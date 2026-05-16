import logging
import sys
from config import BOT_TOKEN, DEEPL_API_KEY, DB_PATH
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

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


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Unhandled exception", exc_info=context.error)


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN not set in .env")

    import os
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    init_db(DB_PATH)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_error_handler(_error_handler)

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang:"))

    # FORWARDED (text only) must come before TEXT: a forwarded text message matches
    # both filters, and the first handler in the same group wins.
    # PHOTO is handled separately so forwarded photos reach photo_handler for OCR.
    app.add_handler(MessageHandler(filters.FORWARDED & ~filters.PHOTO, forwarded_message_handler))
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
