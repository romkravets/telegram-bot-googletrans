# Telegram Translation Bot

Public Telegram bot that translates text, forwarded posts, and photos (OCR).

**Developer:** [Roman Kravets](https://github.com/romkravets)

## Features

- Translates text in private chats and groups
- Translates forwarded posts automatically
- Extracts and translates text from photos (Tesseract OCR)
- DeepL (primary) + Google Translate (fallback)
- 30+ languages, top-10 quick-select buttons
- User language preferences persisted in SQLite

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in BOT_TOKEN and DEEPL_API_KEY
python bot.py
```

## VPS deployment (Ubuntu/Debian)

```bash
# 1. Install Tesseract
sudo apt install tesseract-ocr tesseract-ocr-ukr tesseract-ocr-deu \
  tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-pol tesseract-ocr-chi-sim

# 2. Clone and setup
git clone https://github.com/romkravets/telegram-bot-googletrans /opt/translate-bot
cd /opt/translate-bot
pip3 install -r requirements.txt
cp .env.example .env && nano .env

# 3. Start with PM2
pm2 start ecosystem.config.js
pm2 save
```

## PM2 commands

```bash
pm2 logs translate-bot     # view logs
pm2 restart translate-bot  # restart
pm2 stop translate-bot     # stop
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | From [@BotFather](https://t.me/BotFather) |
| `DEEPL_API_KEY` | optional | [DeepL free tier](https://www.deepl.com/pro-api): 500k chars/month |
| `DB_PATH` | no | SQLite path (default: `./data/translate_bot.db`) |
