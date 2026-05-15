import logging
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
        except Exception as e:
            logging.warning("DeepL failed, falling back to Google: %s", e)
    google_code = lang_info["google"]
    try:
        return GoogleTranslator(source="auto", target=google_code).translate(text)
    except Exception as e:
        logging.error("Google Translate also failed: %s", e)
        raise
