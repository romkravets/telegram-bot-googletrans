import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.storage import get_language
from languages import LANGUAGES
from services.translator import translate
from config import DB_PATH


async def translate_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    if not user:
        return

    text = update.message.text
    chat_type = update.message.chat.type

    if chat_type in ("group", "supergroup"):
        bot_username = context.bot.username
        if not bot_username or f"@{bot_username}" not in text:
            return
        text = text.replace(f"@{bot_username}", "").strip()
        if not text:
            return

    lang_code = await asyncio.to_thread(get_language, user.id, DB_PATH)
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

    try:
        translated = await asyncio.to_thread(translate, text, lang_info)
        await update.message.reply_text(f"🌐 {translated}")
    except Exception:
        logging.exception("Translation failed for user %s", user.id)
        await update.message.reply_text("⚠️ Translation failed. Please try again.")


async def forwarded_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    user = update.effective_user
    if not user:
        return

    # In groups only respond when the bot is explicitly mentioned
    chat_type = update.message.chat.type
    if chat_type in ("group", "supergroup"):
        bot_username = context.bot.username
        combined = (update.message.text or "") + (update.message.caption or "")
        if not bot_username or f"@{bot_username}" not in combined:
            return

    text = update.message.text or update.message.caption
    if not text:
        await update.message.reply_text("⚠️ No text found in the forwarded message.")
        return

    lang_code = await asyncio.to_thread(get_language, user.id, DB_PATH)
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

    try:
        translated = await asyncio.to_thread(translate, text, lang_info)
        await update.message.reply_text(f"🌐 {translated}")
    except Exception:
        logging.exception("Translation failed for user %s", user.id)
        await update.message.reply_text("⚠️ Translation failed. Please try again.")
