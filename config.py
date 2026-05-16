import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
DEEPL_API_KEY: str = os.getenv("DEEPL_API_KEY", "")
DB_PATH: str = os.getenv("DB_PATH", "./data/translate_bot.db")
