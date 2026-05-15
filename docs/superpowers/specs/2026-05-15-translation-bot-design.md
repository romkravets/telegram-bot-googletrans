# Translation Bot — Design Spec
**Date:** 2026-05-15  
**Status:** Approved

---

## Overview

Public Telegram translation bot that works in private chats and groups, translates text and forwarded posts, and extracts + translates text from photos (OCR). Deployed on Hetzner VPS alongside existing blago-bot via PM2, without affecting it.

---

## Architecture

```
VPS Hetzner 157.180.90.223
├── PM2
│   ├── blago-bot (Node.js, polling)   ← untouched
│   └── translate-bot (Python, polling) ← new
├── ZAP (Docker, port 8091)             ← untouched
└── Tesseract OCR (system-installed)
```

**Stack:**
- `python-telegram-bot` v20 — bot framework, polling mode
- `deep-translator` — DeepL primary + Google Translate fallback
- `pytesseract` + `Pillow` — OCR from photos
- `sqlite3` (stdlib) — persist user language preferences
- `PM2` — process management, auto-restart, logs

**Why polling over webhook:** matches blago-bot pattern, no nginx routing needed, simpler VPS setup.

**Why SQLite:** zero-dependency, file-based, ~30 bytes per user record. 100k users ≈ 3 MB. Temp photo files are deleted immediately after OCR processing.

---

## Features

### Commands
| Command | Description |
|---------|-------------|
| `/start` | Welcome message + language selection (top-10 buttons + search) |
| `/lang` | Change language at any time |
| `/lang Polish` | Quick language selection by name |
| `/help` | Short usage guide |

### Text Translation
- **Private chat:** user sends text → bot replies with translation
- **Group chat:** user tags bot `@bot_name text` → bot replies with translation
- **Forwarded post:** auto-detected, translated automatically

### OCR Translation (Photos)
- User sends photo with text → Tesseract extracts text → DeepL/Google translates
- Supported: screenshots, menus, signs, documents, mixed fonts
- Temp file lifecycle: download → OCR → delete (never stored permanently)

### Language Selection UX
```
Quick buttons (top-10):
🇺🇦 UK  🇬🇧 EN  🇩🇪 DE  🇫🇷 FR  🇪🇸 ES
🇮🇹 IT  🇵🇱 PL  🇵🇹 PT  🇨🇳 ZH  🇯🇵 JA

Other languages: user types name → bot searches and confirms
```

### Translation Engine
1. **DeepL API** (primary) — high quality, ~30 languages, free tier 500k chars/month
2. **Google Translate via deep-translator** (fallback) — 130+ languages, activates when DeepL fails or language unsupported
3. Source language: always auto-detected

---

## Data Model

```sql
CREATE TABLE user_settings (
    user_id   INTEGER PRIMARY KEY,
    language  TEXT NOT NULL DEFAULT 'en',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

One row per user. Language stored as ISO 639-1 code (e.g. `uk`, `en`, `de`).

---

## Error Handling

- Translation failure → friendly message in user's language, try fallback engine first
- OCR failure (no text found) → "No text detected in the image"
- Unknown language input → suggest closest match or show language list
- Missing env vars → bot refuses to start with clear error message in logs
- All handlers wrapped in try/except → bot never crashes silently

---

## Deployment

### One-time VPS setup
```bash
# Install Tesseract with language packs
sudo apt install tesseract-ocr tesseract-ocr-ukr tesseract-ocr-deu \
  tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-pol tesseract-ocr-chi-sim

# Clone repo
git clone <repo> /opt/translate-bot
cd /opt/translate-bot

# Install Python dependencies
pip3 install -r requirements.txt

# Create .env
cp .env.example .env
# Fill in BOT_TOKEN and DEEPL_API_KEY
```

### PM2 config (`ecosystem.config.js`)
```js
module.exports = {
  apps: [{
    name: "translate-bot",
    script: "bot.py",
    interpreter: "python3",
    restart_delay: 3000,
    max_restarts: 10,
    env: {
      NODE_ENV: "production"
    }
  }]
}
```

### Commands
```bash
pm2 start ecosystem.config.js   # start
pm2 save                         # persist across VPS reboots
pm2 logs translate-bot           # view logs
pm2 restart translate-bot        # restart
```

**Impact on blago-bot:** zero. Each PM2 process is fully isolated with its own memory, token, and logs.

---

## File Structure

```
telegram-bot-googletrans/
├── bot.py                  # entry point, polling loop, handler registration
├── handlers/
│   ├── start.py            # /start, /lang, /help commands
│   ├── translate.py        # text translation handler
│   └── photo.py            # photo OCR handler
├── services/
│   ├── translator.py       # DeepL + Google fallback logic
│   └── ocr.py              # Tesseract wrapper
├── db/
│   └── storage.py          # SQLite user settings CRUD
├── languages.py            # language list + search
├── ecosystem.config.js     # PM2 config
├── requirements.txt
├── .env.example
└── docs/
    └── superpowers/specs/
        └── 2026-05-15-translation-bot-design.md
```

---

## Environment Variables

```env
BOT_TOKEN=          # Telegram bot token from @BotFather
DEEPL_API_KEY=      # DeepL API key (free tier sufficient to start)
DB_PATH=./data/translate_bot.db
```

---

## Out of Scope (v1)

- Audio/video translation
- Inline mode (`@bot_name` in any chat without adding bot)
- Translation history / stats dashboard
- Webhook mode
- Docker containerization
