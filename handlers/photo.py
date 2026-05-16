import asyncio
import logging
import os
import tempfile
from telegram import Update
from telegram.helpers import escape_markdown
from telegram.ext import ContextTypes
from db.storage import get_language
from languages import LANGUAGES
from services.ocr import extract_text
from services.translator import translate
from config import DB_PATH


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo:
        return

    user = update.effective_user
    if not user:
        return

    # In groups only respond when the bot is mentioned in the caption
    chat_type = update.message.chat.type
    if chat_type in ("group", "supergroup"):
        bot_username = context.bot.username
        caption = update.message.caption or ""
        if not bot_username or f"@{bot_username}" not in caption:
            return

    await update.message.reply_text("📷 Processing image...")

    photo = update.message.photo[-1]  # largest available resolution

    tmp_path: str | None = None
    try:
        # file closed immediately so PTB can write to it via download_to_drive
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            tmp_path = f.name

        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(tmp_path)

        text = await asyncio.to_thread(extract_text, tmp_path)
        if not text:
            await update.message.reply_text("❌ No text detected in the image.")
            return

        lang_code = await asyncio.to_thread(get_language, user.id, DB_PATH)
        lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

        translated = await asyncio.to_thread(translate, text, lang_info)
        safe_text = escape_markdown(text, version=2)
        safe_translated = escape_markdown(translated, version=2)
        await update.message.reply_text(
            f"📝 *Extracted:*\n{safe_text}\n\n🌐 *Translated:*\n{safe_translated}",
            parse_mode="MarkdownV2"
        )
    except Exception:
        logging.exception("Photo handler failed for user %s", user.id)
        await update.message.reply_text("⚠️ Failed to process image. Please try again.")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
