import logging
import os
import tempfile
from telegram import Update
from telegram.ext import ContextTypes
from db.storage import get_language
from languages import LANGUAGES
from services.ocr import extract_text
from services.translator import translate

DB_PATH = os.getenv("DB_PATH", "./data/translate_bot.db")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo:
        return

    user = update.effective_user
    if not user:
        return

    await update.message.reply_text("📷 Processing image...")

    photo = update.message.photo[-1]  # largest available resolution

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        tmp_path = f.name

    try:
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(tmp_path)

        text = extract_text(tmp_path)
        if not text:
            await update.message.reply_text("❌ No text detected in the image.")
            return

        lang_code = get_language(user.id, DB_PATH)
        lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

        translated = translate(text, lang_info)
        await update.message.reply_text(
            f"📝 *Extracted:*\n{text}\n\n🌐 *Translated:*\n{translated}",
            parse_mode="Markdown"
        )
    except Exception:
        logging.exception("Photo handler failed for user %s", user.id)
        await update.message.reply_text("⚠️ Failed to process image. Please try again.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
