# Translation Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public Telegram translation bot that works in private chats and groups, supports DeepL+Google fallback, OCR from photos via Tesseract, and deploys on Hetzner VPS via PM2.

**Architecture:** Python polling bot (python-telegram-bot v20). Pure service modules (translator, ocr, storage) are unit-tested independently. Handlers wire Telegram events to services. SQLite persists user language preferences. PM2 runs the process on VPS alongside blago-bot without interference.

**Tech Stack:** python-telegram-bot==20.3, deepl, deep-translator, pytesseract, Pillow, python-dotenv, sqlite3 (stdlib), pytest, PM2

---

## File Structure

```
telegram-bot-googletrans/
├── bot.py                    # entry point: env validation, handler registration, polling
├── languages.py              # language registry, TOP_10, search function
├── handlers/
│   ├── __init__.py
│   ├── start.py              # /start /lang /help + inline keyboard callback
│   ├── translate.py          # text + forwarded message handlers
│   └── photo.py              # photo OCR handler
├── services/
│   ├── __init__.py
│   ├── translator.py         # DeepL primary + Google fallback
│   └── ocr.py                # Tesseract wrapper
├── db/
│   ├── __init__.py
│   └── storage.py            # SQLite CRUD for user language preferences
├── tests/
│   ├── __init__.py
│   ├── test_languages.py
│   ├── test_storage.py
│   ├── test_translator.py
│   └── test_ocr.py
├── data/
│   └── .gitkeep              # SQLite DB file created here at runtime
├── ecosystem.config.js       # PM2 process config
├── requirements.txt
├── .env.example
└── README.md
```

---

### Task 1: Project scaffold + cleanup

**Files:**
- Delete: `api/webhook.py` (broken webhook code)
- Delete: ` vercel.json` (wrong deployment target, note: has leading space in filename)
- Replace: `requirements.txt`
- Create: `.env.example`, `data/.gitkeep`, `tests/__init__.py`, `handlers/__init__.py`, `services/__init__.py`, `db/__init__.py`
- Update: `.gitignore`

- [ ] **Step 1: Remove old broken files**

```bash
rm "/Users/romkravets/Documents/GitHub/telegram-bot-googletrans/api/webhook.py"
rm "/Users/romkravets/Documents/GitHub/telegram-bot-googletrans/ vercel.json"
rmdir "/Users/romkravets/Documents/GitHub/telegram-bot-googletrans/api"
```

- [ ] **Step 2: Replace requirements.txt**

Content of `requirements.txt`:
```
python-telegram-bot==20.3
deepl==1.18.0
deep-translator==1.11.4
pytesseract==0.3.10
Pillow==10.3.0
python-dotenv==1.0.1
pytest==8.2.0
```

- [ ] **Step 3: Create .env.example**

Content of `.env.example`:
```env
BOT_TOKEN=your_telegram_bot_token_from_botfather
DEEPL_API_KEY=your_deepl_api_key_from_deepl.com
DB_PATH=./data/translate_bot.db
```

- [ ] **Step 4: Update .gitignore**

Content of `.gitignore`:
```gitignore
.env
data/*.db
__pycache__/
*.pyc
*.pyo
.pytest_cache/
```

- [ ] **Step 5: Create directory structure and empty init files**

```bash
cd /path/to/telegram-bot-googletrans
mkdir -p handlers services db tests data
touch handlers/__init__.py services/__init__.py db/__init__.py tests/__init__.py data/.gitkeep
```

- [ ] **Step 6: Commit scaffold**

```bash
git add -A
git commit -m "chore: scaffold new project structure, remove broken webhook code"
```

---

### Task 2: languages.py — Language registry and search

**Files:**
- Create: `languages.py`
- Create: `tests/test_languages.py`

- [ ] **Step 1: Write failing tests**

Content of `tests/test_languages.py`:
```python
from languages import search_language, LANGUAGES, TOP_10_CODES

def test_search_exact_english_name():
    result = search_language("Polish")
    assert result == "pl"

def test_search_case_insensitive():
    result = search_language("polish")
    assert result == "pl"

def test_search_partial_match():
    result = search_language("Germ")
    assert result == "de"

def test_search_by_code():
    result = search_language("uk")
    assert result == "uk"

def test_search_unknown_language():
    result = search_language("Klingon")
    assert result is None

def test_top10_codes_are_valid():
    for code in TOP_10_CODES:
        assert code in LANGUAGES

def test_language_has_required_fields():
    for code, info in LANGUAGES.items():
        assert "name" in info, f"{code} missing 'name'"
        assert "flag" in info, f"{code} missing 'flag'"
        assert "deepl" in info, f"{code} missing 'deepl'"
        assert "google" in info, f"{code} missing 'google'"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_languages.py -v
```
Expected: `ModuleNotFoundError: No module named 'languages'`

- [ ] **Step 3: Write languages.py**

Content of `languages.py`:
```python
from typing import Optional

# deepl=None means language is Google-only (DeepL doesn't support it)
LANGUAGES: dict[str, dict] = {
    "uk": {"name": "Ukrainian",  "flag": "🇺🇦", "deepl": "UK",    "google": "uk"},
    "en": {"name": "English",    "flag": "🇬🇧", "deepl": "EN-GB", "google": "en"},
    "de": {"name": "German",     "flag": "🇩🇪", "deepl": "DE",    "google": "de"},
    "fr": {"name": "French",     "flag": "🇫🇷", "deepl": "FR",    "google": "fr"},
    "es": {"name": "Spanish",    "flag": "🇪🇸", "deepl": "ES",    "google": "es"},
    "it": {"name": "Italian",    "flag": "🇮🇹", "deepl": "IT",    "google": "it"},
    "pl": {"name": "Polish",     "flag": "🇵🇱", "deepl": "PL",    "google": "pl"},
    "pt": {"name": "Portuguese", "flag": "🇵🇹", "deepl": "PT-PT", "google": "pt"},
    "zh": {"name": "Chinese",    "flag": "🇨🇳", "deepl": "ZH",    "google": "zh-CN"},
    "ja": {"name": "Japanese",   "flag": "🇯🇵", "deepl": "JA",    "google": "ja"},
    "ko": {"name": "Korean",     "flag": "🇰🇷", "deepl": "KO",    "google": "ko"},
    "ru": {"name": "Russian",    "flag": "🇷🇺", "deepl": "RU",    "google": "ru"},
    "ar": {"name": "Arabic",     "flag": "🇸🇦", "deepl": "AR",    "google": "ar"},
    "nl": {"name": "Dutch",      "flag": "🇳🇱", "deepl": "NL",    "google": "nl"},
    "sv": {"name": "Swedish",    "flag": "🇸🇪", "deepl": "SV",    "google": "sv"},
    "da": {"name": "Danish",     "flag": "🇩🇰", "deepl": "DA",    "google": "da"},
    "fi": {"name": "Finnish",    "flag": "🇫🇮", "deepl": "FI",    "google": "fi"},
    "cs": {"name": "Czech",      "flag": "🇨🇿", "deepl": "CS",    "google": "cs"},
    "sk": {"name": "Slovak",     "flag": "🇸🇰", "deepl": "SK",    "google": "sk"},
    "ro": {"name": "Romanian",   "flag": "🇷🇴", "deepl": "RO",    "google": "ro"},
    "hu": {"name": "Hungarian",  "flag": "🇭🇺", "deepl": "HU",    "google": "hu"},
    "bg": {"name": "Bulgarian",  "flag": "🇧🇬", "deepl": "BG",    "google": "bg"},
    "el": {"name": "Greek",      "flag": "🇬🇷", "deepl": "EL",    "google": "el"},
    "tr": {"name": "Turkish",    "flag": "🇹🇷", "deepl": "TR",    "google": "tr"},
    "id": {"name": "Indonesian", "flag": "🇮🇩", "deepl": "ID",    "google": "id"},
    "nb": {"name": "Norwegian",  "flag": "🇳🇴", "deepl": "NB",    "google": "no"},
    # Google-only languages
    "hi": {"name": "Hindi",      "flag": "🇮🇳", "deepl": None,    "google": "hi"},
    "vi": {"name": "Vietnamese", "flag": "🇻🇳", "deepl": None,    "google": "vi"},
    "th": {"name": "Thai",       "flag": "🇹🇭", "deepl": None,    "google": "th"},
    "he": {"name": "Hebrew",     "flag": "🇮🇱", "deepl": None,    "google": "iw"},
    "fa": {"name": "Persian",    "flag": "🇮🇷", "deepl": None,    "google": "fa"},
}

TOP_10_CODES = ["uk", "en", "de", "fr", "es", "it", "pl", "pt", "zh", "ja"]


def search_language(query: str) -> Optional[str]:
    q = query.strip().lower()
    for code, info in LANGUAGES.items():
        if code == q or info["name"].lower().startswith(q):
            return code
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_languages.py -v
```
Expected: all 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add languages.py tests/test_languages.py
git commit -m "feat: add language registry with DeepL/Google codes and search"
```

---

### Task 3: db/storage.py — SQLite user settings

**Files:**
- Create: `db/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Write failing tests**

Content of `tests/test_storage.py`:
```python
import tempfile
import os
from db.storage import init_db, get_language, set_language

def make_db():
    tmp = tempfile.mktemp(suffix=".db")
    init_db(tmp)
    return tmp

def test_default_language_is_en():
    db = make_db()
    assert get_language(123, db) == "en"
    os.unlink(db)

def test_set_and_get_language():
    db = make_db()
    set_language(123, "uk", db)
    assert get_language(123, db) == "uk"
    os.unlink(db)

def test_update_existing_language():
    db = make_db()
    set_language(123, "uk", db)
    set_language(123, "de", db)
    assert get_language(123, db) == "de"
    os.unlink(db)

def test_different_users_are_independent():
    db = make_db()
    set_language(1, "uk", db)
    set_language(2, "fr", db)
    assert get_language(1, db) == "uk"
    assert get_language(2, db) == "fr"
    os.unlink(db)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_storage.py -v
```
Expected: `ModuleNotFoundError: No module named 'db.storage'`

- [ ] **Step 3: Write db/storage.py**

Content of `db/storage.py`:
```python
import sqlite3


def init_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id    INTEGER PRIMARY KEY,
                language   TEXT NOT NULL DEFAULT 'en',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def get_language(user_id: int, db_path: str) -> str:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT language FROM user_settings WHERE user_id = ?", (user_id,)
        ).fetchone()
    return row[0] if row else "en"


def set_language(user_id: int, lang_code: str, db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO user_settings (user_id, language, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                language = excluded.language,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, lang_code))
        conn.commit()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_storage.py -v
```
Expected: all 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add db/storage.py tests/test_storage.py
git commit -m "feat: add SQLite user settings storage"
```

---

### Task 4: services/translator.py — DeepL + Google fallback

**Files:**
- Create: `services/translator.py`
- Create: `tests/test_translator.py`

- [ ] **Step 1: Write failing tests**

Content of `tests/test_translator.py`:
```python
from unittest.mock import patch, MagicMock
from services.translator import translate

def test_translate_uses_deepl_when_available():
    lang_info = {"deepl": "DE", "google": "de"}
    with patch("services.translator.DEEPL_API_KEY", "fake_key"):
        with patch("services.translator.deepl.Translator") as mock_cls:
            mock_t = MagicMock()
            mock_t.translate_text.return_value = MagicMock(text="Hallo")
            mock_cls.return_value = mock_t
            result = translate("Hello", lang_info)
    assert result == "Hallo"

def test_translate_falls_back_to_google_when_deepl_raises():
    lang_info = {"deepl": "DE", "google": "de"}
    with patch("services.translator.DEEPL_API_KEY", "fake_key"):
        with patch("services.translator.deepl.Translator") as mock_cls:
            mock_t = MagicMock()
            mock_t.translate_text.side_effect = Exception("quota exceeded")
            mock_cls.return_value = mock_t
            with patch("services.translator.GoogleTranslator") as mock_g_cls:
                mock_g = MagicMock()
                mock_g.translate.return_value = "Hallo"
                mock_g_cls.return_value = mock_g
                result = translate("Hello", lang_info)
    assert result == "Hallo"

def test_translate_uses_google_when_deepl_code_is_none():
    lang_info = {"deepl": None, "google": "hi"}
    with patch("services.translator.GoogleTranslator") as mock_g_cls:
        mock_g = MagicMock()
        mock_g.translate.return_value = "नमस्ते"
        mock_g_cls.return_value = mock_g
        result = translate("Hello", lang_info)
    assert result == "नमस्ते"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_translator.py -v
```
Expected: `ModuleNotFoundError: No module named 'services.translator'`

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 4: Write services/translator.py**

Content of `services/translator.py`:
```python
import os
import deepl
from deep_translator import GoogleTranslator

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")


def translate(text: str, lang_info: dict) -> str:
    if lang_info.get("deepl") and DEEPL_API_KEY:
        try:
            translator = deepl.Translator(DEEPL_API_KEY)
            result = translator.translate_text(text, target_lang=lang_info["deepl"])
            return result.text
        except Exception:
            pass
    google_code = lang_info["google"]
    return GoogleTranslator(source="auto", target=google_code).translate(text)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_translator.py -v
```
Expected: all 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add services/translator.py tests/test_translator.py
git commit -m "feat: add translator service with DeepL primary and Google fallback"
```

---

### Task 5: services/ocr.py — Tesseract OCR wrapper

**Files:**
- Create: `services/ocr.py`
- Create: `tests/test_ocr.py`

- [ ] **Step 1: Write failing tests**

Content of `tests/test_ocr.py`:
```python
from unittest.mock import patch
from services.ocr import extract_text

def test_extract_text_returns_string():
    with patch("services.ocr.Image.open"):
        with patch("services.ocr.pytesseract.image_to_string", return_value="Hello World"):
            result = extract_text("/fake/path.jpg")
    assert result == "Hello World"

def test_extract_text_returns_none_when_empty():
    with patch("services.ocr.Image.open"):
        with patch("services.ocr.pytesseract.image_to_string", return_value="   \n  "):
            result = extract_text("/fake/path.jpg")
    assert result is None

def test_extract_text_returns_none_on_error():
    with patch("services.ocr.Image.open"):
        with patch("services.ocr.pytesseract.image_to_string", side_effect=Exception("tesseract not found")):
            result = extract_text("/fake/path.jpg")
    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_ocr.py -v
```
Expected: `ModuleNotFoundError: No module named 'services.ocr'`

- [ ] **Step 3: Write services/ocr.py**

Content of `services/ocr.py`:
```python
from typing import Optional
import pytesseract
from PIL import Image


def extract_text(image_path: str) -> Optional[str]:
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img).strip()
        return text if text else None
    except Exception:
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_ocr.py -v
```
Expected: all 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add services/ocr.py tests/test_ocr.py
git commit -m "feat: add Tesseract OCR service wrapper"
```

---

### Task 6: handlers/start.py — /start, /lang, /help + language keyboard

**Files:**
- Create: `handlers/start.py`

Note: Telegram handler functions require a live bot to test. Verify manually in Step 2.

- [ ] **Step 1: Write handlers/start.py**

Content of `handlers/start.py`:
```python
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

    if query.data == "lang:search":
        await query.edit_message_text(
            "Type the language name:\n`/lang Arabic` or `/lang Hindi`",
            parse_mode="Markdown"
        )
        return

    code = query.data.split(":")[1]
    if code in LANGUAGES:
        set_language(update.effective_user.id, code, DB_PATH)
        info = LANGUAGES[code]
        await query.edit_message_text(
            f"✅ Language set to {info['flag']} {info['name']}\n\n"
            "Now send me any text or photo to translate!"
        )
```

- [ ] **Step 2: Commit**

```bash
git add handlers/start.py
git commit -m "feat: add /start /lang /help handlers with inline language keyboard"
```

---

### Task 7: handlers/translate.py — Text and forwarded message translation

**Files:**
- Create: `handlers/translate.py`

- [ ] **Step 1: Write handlers/translate.py**

Content of `handlers/translate.py`:
```python
import os
from telegram import Update
from telegram.ext import ContextTypes
from db.storage import get_language
from languages import LANGUAGES
from services.translator import translate

DB_PATH = os.getenv("DB_PATH", "./data/translate_bot.db")


async def translate_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    text = update.message.text
    chat_type = update.message.chat.type

    if chat_type in ("group", "supergroup"):
        bot_username = context.bot.username
        if f"@{bot_username}" not in text:
            return
        text = text.replace(f"@{bot_username}", "").strip()
        if not text:
            return

    lang_code = get_language(update.effective_user.id, DB_PATH)
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

    try:
        translated = translate(text, lang_info)
        await update.message.reply_text(f"🌐 {translated}")
    except Exception:
        await update.message.reply_text("⚠️ Translation failed. Please try again.")


async def forwarded_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    text = update.message.text or update.message.caption
    if not text:
        await update.message.reply_text("⚠️ No text found in the forwarded message.")
        return

    lang_code = get_language(update.effective_user.id, DB_PATH)
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

    try:
        translated = translate(text, lang_info)
        await update.message.reply_text(f"🌐 {translated}")
    except Exception:
        await update.message.reply_text("⚠️ Translation failed. Please try again.")
```

- [ ] **Step 2: Commit**

```bash
git add handlers/translate.py
git commit -m "feat: add text and forwarded message translation handlers"
```

---

### Task 8: handlers/photo.py — OCR photo translation

**Files:**
- Create: `handlers/photo.py`

- [ ] **Step 1: Write handlers/photo.py**

Content of `handlers/photo.py`:
```python
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

        lang_code = get_language(update.effective_user.id, DB_PATH)
        lang_info = LANGUAGES.get(lang_code, LANGUAGES["en"])

        translated = translate(text, lang_info)
        await update.message.reply_text(
            f"📝 *Extracted:*\n{text}\n\n🌐 *Translated:*\n{translated}",
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text("⚠️ Failed to process image. Please try again.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
```

- [ ] **Step 2: Commit**

```bash
git add handlers/photo.py
git commit -m "feat: add photo OCR handler with Tesseract + translation"
```

---

### Task 9: bot.py — Entry point, handler registration, polling

**Files:**
- Create: `bot.py`

- [ ] **Step 1: Write bot.py**

Content of `bot.py`:
```python
import os
import sys
import logging
from dotenv import load_dotenv
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DB_PATH = os.getenv("DB_PATH", "./data/translate_bot.db")

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set in .env", file=sys.stderr)
    sys.exit(1)

if not DEEPL_API_KEY:
    print("WARNING: DEEPL_API_KEY not set — using Google Translate only", file=sys.stderr)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

from db.storage import init_db
from handlers.start import start_command, lang_command, help_command, language_callback
from handlers.translate import translate_text_handler, forwarded_message_handler
from handlers.photo import photo_handler


def main() -> None:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    init_db(DB_PATH)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang:"))

    # FORWARDED before TEXT: a forwarded text message matches both filters,
    # first registered handler wins within the same group
    app.add_handler(MessageHandler(filters.FORWARDED, forwarded_message_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    logging.info("Bot started. Polling...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run full test suite**

```bash
python -m pytest tests/ -v
```
Expected: all 17 tests PASS

- [ ] **Step 3: Smoke test locally**

```bash
cp .env.example .env
# Edit .env: set real BOT_TOKEN and DEEPL_API_KEY
python bot.py
```

Expected output:
```
2026-05-15 12:00:00 [INFO] Bot started. Polling...
```

Manual checks in Telegram:
1. `/start` → language keyboard with 10 buttons appears
2. Tap "🇺🇦 Ukrainian" → "✅ Language set to 🇺🇦 Ukrainian"
3. Send "Hello" → "🌐 Привіт"
4. Forward any post → bot translates it
5. Send a photo with text → "📷 Processing image..." then translation
6. `/lang Polish` → "✅ Language set to 🇵🇱 Polish"
7. `/help` → usage guide with GitHub link

- [ ] **Step 4: Commit**

```bash
git add bot.py
git commit -m "feat: add bot entry point with handler registration and polling"
```

---

### Task 10: ecosystem.config.js + README

**Files:**
- Create: `ecosystem.config.js`
- Replace: `README.md`

- [ ] **Step 1: Write ecosystem.config.js**

Content of `ecosystem.config.js`:
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

- [ ] **Step 2: Write README.md**

Content of `README.md`:
```markdown
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
```

- [ ] **Step 3: Run final test suite**

```bash
python -m pytest tests/ -v
```
Expected: all 17 tests PASS

- [ ] **Step 4: Final commit**

```bash
git add ecosystem.config.js README.md
git commit -m "chore: add PM2 config and deployment README"
```

---

## Deployment checklist (run on VPS after all tasks complete)

```bash
# On VPS as root or sudo user:
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-ukr tesseract-ocr-deu \
  tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-pol tesseract-ocr-chi-sim

git clone https://github.com/romkravets/telegram-bot-googletrans /opt/translate-bot
cd /opt/translate-bot
pip3 install -r requirements.txt
cp .env.example .env
nano .env  # set BOT_TOKEN and DEEPL_API_KEY

pm2 start ecosystem.config.js
pm2 save
pm2 logs translate-bot  # verify "Bot started. Polling..."
```

Verify blago-bot still running: `pm2 list` — both processes should show "online".
