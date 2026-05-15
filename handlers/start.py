import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.storage import get_language, set_language
from languages import LANGUAGES, TOP_10_CODES, search_language

DB_PATH = os.getenv("DB_PATH", "./data/translate_bot.db")


def _language_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for code in TOP_10_CODES:
        info = LANGUAGES[code]
        row.append(InlineKeyboardButton(
            f"{info['flag']} {info['name']}",
            callback_data=f"lang:{code}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔍 Other language", callback_data="lang:search")])
    return InlineKeyboardMarkup(buttons)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hello! I translate text, forwarded posts, and photos.\n\n"
        "Choose your target language:",
        reply_markup=_language_keyboard()
    )


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        query = " ".join(context.args)
        code = search_language(query)
        if code:
            set_language(update.effective_user.id, code, DB_PATH)
            info = LANGUAGES[code]
            await update.message.reply_text(
                f"✅ Language set to {info['flag']} {info['name']}"
            )
        else:
            await update.message.reply_text(
                f"❌ Language '{query}' not found.\n"
                "Try: /lang Polish or /lang Japanese"
            )
    else:
        await update.message.reply_text(
            "Choose your target language:",
            reply_markup=_language_keyboard()
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 *How to use:*\n\n"
        "• Send any text → I translate it\n"
        "• Forward a post → I translate it\n"
        "• Send a photo with text → I read and translate it\n"
        "• In groups: mention me `@bot_name your text`\n\n"
        "⚙️ *Commands:*\n"
        "/start — choose language\n"
        "/lang — change language\n"
        "/lang Polish — set language directly\n"
        "/help — this message\n\n"
        "👨‍💻 [github.com/romkravets](https://github.com/romkravets)",
        parse_mode="Markdown"
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not update.effective_user:
        await query.edit_message_text("❌ Cannot identify user.")
        return

    if query.data == "lang:search":
        await query.edit_message_text(
            "Type the language name:\n`/lang Arabic` or `/lang Hindi`",
            parse_mode="Markdown"
        )
        return

    code = query.data.removeprefix("lang:")
    if code in LANGUAGES:
        set_language(update.effective_user.id, code, DB_PATH)
        info = LANGUAGES[code]
        await query.edit_message_text(
            f"✅ Language set to {info['flag']} {info['name']}\n\n"
            "Now send me any text or photo to translate!"
        )
    else:
        await query.edit_message_text("❌ Unknown language. Use /lang to choose again.")
