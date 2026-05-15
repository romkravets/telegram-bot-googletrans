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
