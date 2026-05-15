import os
from telegram import Update
from telegram.ext import ContextTypes
from db.storage import get_language
from languages import LANGUAGES
from services.translator import translate

DB_PATH = os.getenv("DB_PATH", "./data/translate_bot.db")


async def translate_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    text = update.message.text
    chat_type = update.message.chat.type

    if chat_type in ("group", "supergroup"):
        bot_username = context.bot.username
        if f"@{bot_username}" not in text:
            return
        text = text.replace(f"@{bot_username}", "").strip()
        if not text:
            return

    lang_code = get_language(update.effective_user.id, DB_PATH)
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

    try:
        translated = translate(text, lang_info)
        await update.message.reply_text(f"🌐 {translated}")
    except Exception:
        await update.message.reply_text("⚠️ Translation failed. Please try again.")


async def forwarded_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    text = update.message.text or update.message.caption
    if not text:
        await update.message.reply_text("⚠️ No text found in the forwarded message.")
        return

    lang_code = get_language(update.effective_user.id, DB_PATH)
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

    try:
        translated = translate(text, lang_info)
        await update.message.reply_text(f"🌐 {translated}")
    except Exception:
        await update.message.reply_text("⚠️ Translation failed. Please try again.")
