from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
translator = GoogleTranslator(source="auto", target="en")
user_languages = {}

telegram_app = Application.builder().token(BOT_TOKEN).build()


@telegram_app.command_handler("start")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["en", "uk", "es", "fr", "de"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Оберіть вашу мову перекладу:", reply_markup=reply_markup)

@telegram_app.message_handler(filters.Regex("^(en|uk|es|fr|de)$"))
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_languages[update.message.from_user.id] = update.message.text
    await update.message.reply_text(f"Ви обрали мову: {update.message.text}")

@telegram_app.message_handler(filters.TEXT & ~filters.COMMAND)
async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_languages:
        target_lang = user_languages[user_id]
        translated_text = GoogleTranslator(source="auto", target=target_lang).translate(update.message.text)
        await update.message.reply_text(f"Переклад: {translated_text}")
    else:
        await update.message.reply_text("Спочатку виберіть мову через /start.")

@telegram_app.message_handler(filters.FORWARDED)
async def translate_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_languages:
        target_lang = user_languages[user_id]
        if update.message.text:
            translated_text = GoogleTranslator(source="auto", target=target_lang).translate(update.message.text)
            await update.message.reply_text(f"Переклад:\n{translated_text}")
        elif update.message.caption:
            translated_text = GoogleTranslator(source="auto", target=target_lang).translate(update.message.caption)
            await update.message.reply_text(f"Переклад підпису:\n{translated_text}")
    else:
        await update.message.reply_text("Спочатку виберіть мову через /start.")

@app.post("/")
async def telegram_webhook(request: Request):
    update_data = await request.json()
    update = Update.de_json(update_data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
