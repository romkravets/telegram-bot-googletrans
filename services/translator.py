import logging
import threading
import deepl
from deep_translator import GoogleTranslator
from languages import LanguageInfo
from config import DEEPL_API_KEY

# Thread-local DeepL instance: each asyncio.to_thread worker gets its own session
_local = threading.local()


def _get_deepl() -> deepl.Translator | None:
    if not DEEPL_API_KEY:
        return None
    if not hasattr(_local, "translator"):
        _local.translator = deepl.Translator(DEEPL_API_KEY)
    return _local.translator


def translate(text: str, lang_info: LanguageInfo) -> str:
    deepl_translator = _get_deepl()
    if lang_info.get("deepl") and deepl_translator:
        try:
            result = deepl_translator.translate_text(text, target_lang=lang_info["deepl"])
            return result.text
        except Exception as e:
            logging.warning("DeepL failed, falling back to Google: %s", e)
    google_code = lang_info["google"]
    try:
        result = GoogleTranslator(source="auto", target=google_code).translate(text)
        if not result:
            raise ValueError(f"Google Translate returned empty result for: {text[:50]!r}")
        return result
    except Exception as e:
        logging.error("Google Translate also failed: %s", e)
        raise
