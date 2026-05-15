from typing import Optional, TypedDict


class LanguageInfo(TypedDict):
    name: str
    flag: str
    deepl: str | None
    google: str


# deepl=None means language is Google-only (DeepL doesn't support it)
LANGUAGES: dict[str, LanguageInfo] = {
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
    "nb": {"name": "Norwegian",  "flag": "🇳🇴", "deepl": "NB",    "google": "no"},  # nb=Bokmål; "no" also found via name prefix
    # Google-only languages
    "hi": {"name": "Hindi",      "flag": "🇮🇳", "deepl": None,    "google": "hi"},
    "vi": {"name": "Vietnamese", "flag": "🇻🇳", "deepl": None,    "google": "vi"},
    "th": {"name": "Thai",       "flag": "🇹🇭", "deepl": None,    "google": "th"},
    "he": {"name": "Hebrew",     "flag": "🇮🇱", "deepl": None,    "google": "iw"},
    "fa": {"name": "Persian",    "flag": "🇮🇷", "deepl": None,    "google": "fa"},
}

TOP_10_CODES: list[str] = ["uk", "en", "de", "fr", "es", "it", "pl", "pt", "zh", "ja"]


def search_language(query: str) -> Optional[str]:
    """Return ISO code for query (exact code or name prefix, case-insensitive). None if not found."""
    q = query.strip().lower()
    if not q:
        return None
    for code, info in LANGUAGES.items():
        if code == q or info["name"].lower().startswith(q):
            return code
    return None
