import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

translator = GoogleTranslator(source="auto", target="en")

user_languages = {}

# Команда старту
async def start(update: Update, context: CallbackContext):
    keyboard = [["en", "uk", "es", "fr", "de"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("Оберіть вашу мову перекладу:", reply_markup=reply_markup)

async def set_language(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    selected_language = update.message.text

    user_languages[user_id] = selected_language
    await update.message.reply_text(f"Ви обрали мову: {selected_language}")

async def translate_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_languages:
        target_lang = user_languages[user_id]
        translator = GoogleTranslator(source="auto", target=target_lang)  # Correct initialization
        translated_text = translator.translate(update.message.text)
        await update.message.reply_text(f"Переклад: {translated_text}")
    else:
        await update.message.reply_text("Спочатку виберіть мову через /start.")

async def translate_forwarded_message(update: Update, context: CallbackContext):
    """Переклад пересланих повідомлень, включаючи текст у зображеннях"""
    if update.message.forward_origin:
        user_id = update.message.from_user.id

        if user_id in user_languages:
            target_lang = user_languages[user_id]
            translator = GoogleTranslator(source="auto", target=target_lang)

            if update.message.text:
                translated_text = translator.translate(update.message.text)
                await update.message.reply_text(f"Переклад:\n{translated_text}")
            elif update.message.caption:
                translated_text = translator.translate(update.message.caption)
                await update.message.reply_text(f"Переклад підпису:\n{translated_text}")
        else:
            await update.message.reply_text("Спочатку виберіть мову через /start.")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Regex("^(en|uk|es|fr|de)$"), set_language))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
app.add_handler(MessageHandler(filters.FORWARDED, translate_forwarded_message))

app.run_polling()
