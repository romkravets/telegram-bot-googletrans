import asyncio
import logging
import uuid
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes
from db.storage import get_language
from languages import LANGUAGES
from services.translator import translate
from config import DB_PATH


async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query
    if not query:
        return

    text = query.query.strip()
    if not text:
        await query.answer(
            [],
            cache_time=0,
            switch_pm_text="Type text to translate",
            switch_pm_parameter="start",
        )
        return

    user = query.from_user
    lang_code = await asyncio.to_thread(get_language, user.id, DB_PATH)
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

    try:
        translated = await asyncio.to_thread(translate, text, lang_info)
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{lang_info['flag']} {lang_info['name']}",
                description=translated[:120],
                input_message_content=InputTextMessageContent(f"🌐 {translated}"),
            )
        ]
        await query.answer(results, cache_time=30)
    except Exception:
        logging.exception("Inline query failed for user %s", user.id)
        await query.answer([], cache_time=0)
