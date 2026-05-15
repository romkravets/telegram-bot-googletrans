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
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in BOT_TOKEN and DEEPL_API_KEY in .env
python3 bot.py
```

## VPS deployment (Ubuntu/Debian)

```bash
# 1. Install Node.js + PM2 (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pm2

# 2. Install Tesseract with language packs
# Add more tesseract-ocr-* packages for additional languages
sudo apt install tesseract-ocr tesseract-ocr-ukr tesseract-ocr-deu \
  tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-pol tesseract-ocr-chi-sim

# 3. Clone and setup
git clone https://github.com/romkravets/telegram-bot-googletrans /opt/translate-bot
cd /opt/translate-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env

# 4. Start with PM2 and enable auto-start on reboot
pm2 start ecosystem.config.js
pm2 startup systemd
pm2 save
```

## PM2 commands

```bash
pm2 logs translate-bot     # view logs
pm2 restart translate-bot  # restart
pm2 stop translate-bot     # stop
pm2 list                   # show all running bots
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | From [@BotFather](https://t.me/BotFather) |
| `DEEPL_API_KEY` | optional | [DeepL free tier](https://www.deepl.com/pro-api): 500k chars/month |
| `DB_PATH` | no | SQLite path (default: `./data/translate_bot.db`) |
