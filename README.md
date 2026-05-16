# Telegram Translation Bot

A public Telegram bot that translates text, forwarded posts, and photos — right where you are.

**Developer:** [Roman Kravets](https://github.com/romkravets)

---

## Features

| Feature | Description |
|---------|-------------|
| 💬 Text translation | Send any text — get an instant translation |
| 📨 Forwarded posts | Forward a channel post or message — bot translates it automatically |
| 📷 Photo OCR | Send a photo with text — bot extracts and translates it via Tesseract |
| ✍️ Inline mode | Type `@botname text` in **any** chat — see translation without leaving |
| 👥 Group support | Mention the bot `@botname your text` in any group |
| 🌐 30+ languages | DeepL (primary) + Google Translate (fallback) |
| 💾 Preferences | Per-user language saved in SQLite — remembered across sessions |

---

## How to use

### Private chat
Just send any text, forward a post, or send a photo with text.

### Groups
Mention the bot with your text:
```
@YourBotName Привіт, як справи?
```
For forwarded posts in groups — mention must appear in the caption.

### Inline mode (translate anywhere)
Type `@YourBotName` followed by a space and your text **in any chat**:
```
@YourBotName The quick brown fox jumps over the lazy dog
```
A translation result will appear as a popup — tap it to send.
This is the fastest way to translate without switching chats.

### Commands
| Command | Description |
|---------|-------------|
| `/start` | Welcome message + choose target language |
| `/lang` | Open language picker |
| `/lang Polish` | Set language directly by name |
| `/help` | Show this usage guide |

---

## Supported languages

DeepL (high quality) + Google Translate (fallback for all languages):

🇺🇦 Ukrainian · 🇬🇧 English · 🇩🇪 German · 🇫🇷 French · 🇪🇸 Spanish · 🇮🇹 Italian · 🇵🇱 Polish · 🇵🇹 Portuguese · 🇨🇳 Chinese · 🇯🇵 Japanese · 🇰🇷 Korean · 🇷🇺 Russian · 🇸🇦 Arabic · 🇳🇱 Dutch · 🇸🇪 Swedish · 🇩🇰 Danish · 🇫🇮 Finnish · 🇨🇿 Czech · 🇸🇰 Slovak · 🇷🇴 Romanian · 🇭🇺 Hungarian · 🇧🇬 Bulgarian · 🇬🇷 Greek · 🇹🇷 Turkish · 🇮🇩 Indonesian · 🇳🇴 Norwegian · 🇮🇳 Hindi · 🇻🇳 Vietnamese · 🇹🇭 Thai · 🇮🇱 Hebrew · 🇮🇷 Persian

---

## Architecture

```
telegram-bot-googletrans/
├── bot.py                  # Entry point: registers all handlers, starts polling
├── config.py               # Centralised env var loading (BOT_TOKEN, DEEPL_API_KEY, DB_PATH)
├── languages.py            # Language registry (31 languages, DeepL + Google codes)
├── handlers/
│   ├── start.py            # /start, /lang, /help commands + language keyboard callback
│   ├── translate.py        # Text and forwarded message handlers
│   ├── photo.py            # Photo handler: download → OCR → translate
│   └── inline.py           # Inline query handler (@botname text in any chat)
├── services/
│   ├── translator.py       # DeepL (thread-local singleton) + Google fallback
│   └── ocr.py              # Tesseract OCR via pytesseract + Pillow
├── db/
│   └── storage.py          # SQLite: init, get_language, set_language
├── tests/                  # 20 unit tests (languages, storage, OCR, translator)
├── ecosystem.config.js     # PM2 process config for VPS deployment
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Dev dependencies (adds pytest)
```

All blocking I/O (SQLite, HTTP translation requests, Tesseract OCR) runs via `asyncio.to_thread` so the event loop is never blocked.

---

## Local development

### Prerequisites
- Python 3.10+
- Tesseract OCR installed

Install Tesseract (macOS):
```bash
brew install tesseract
```

Install Tesseract (Ubuntu/Debian):
```bash
sudo apt install tesseract-ocr tesseract-ocr-ukr tesseract-ocr-deu \
  tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-pol tesseract-ocr-chi-sim
```

### Setup

```bash
git clone https://github.com/romkravets/telegram-bot-googletrans
cd telegram-bot-googletrans

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements-dev.txt   # includes pytest
cp .env.example .env
# edit .env: fill in BOT_TOKEN and optionally DEEPL_API_KEY
```

### Run tests

```bash
pytest
```

### Start the bot

```bash
python3 bot.py
```

---

## Enable inline mode (required for @botname in any chat)

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/setinline`
3. Choose your bot
4. Enter a placeholder hint, e.g. `Enter text to translate...`

That's it. No code changes needed — the bot already handles inline queries.

---

## VPS deployment (Ubuntu/Debian + PM2)

### 1. Install Node.js + PM2

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pm2
```

### 2. Install Tesseract

```bash
sudo apt install tesseract-ocr tesseract-ocr-ukr tesseract-ocr-deu \
  tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-pol tesseract-ocr-chi-sim
```

Add more packs as needed: `tesseract-ocr-jpn`, `tesseract-ocr-chi-sim`, etc.

### 3. Clone and configure

```bash
git clone https://github.com/romkravets/telegram-bot-googletrans /opt/translate-bot
cd /opt/translate-bot

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # fill in BOT_TOKEN and DEEPL_API_KEY
```

### 4. Start with PM2 and enable auto-start on reboot

```bash
pm2 start ecosystem.config.js
pm2 startup systemd
pm2 save
```

### PM2 commands

```bash
pm2 logs translate-bot      # live logs
pm2 restart translate-bot   # restart
pm2 stop translate-bot      # stop
pm2 list                    # all running processes
```

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | From [@BotFather](https://t.me/BotFather) |
| `DEEPL_API_KEY` | optional | [DeepL free tier](https://www.deepl.com/pro-api): 500k chars/month. If not set, falls back to Google Translate for all requests |
| `DB_PATH` | optional | SQLite file path (default: `./data/translate_bot.db`) |

---

## Tech stack

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v22 — async bot framework
- [DeepL Python SDK](https://github.com/DeepLcom/deepl-python) — primary translation engine
- [deep-translator](https://github.com/nidhaloff/deep-translator) — Google Translate fallback
- [pytesseract](https://github.com/madmaze/pytesseract) + [Pillow](https://python-pillow.org/) — OCR
- SQLite (stdlib) — user language preferences
- [PM2](https://pm2.keymetrics.io/) — process manager for VPS
