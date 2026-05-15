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
