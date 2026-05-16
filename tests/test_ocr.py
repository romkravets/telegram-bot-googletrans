from unittest.mock import patch
from services.ocr import extract_text

def _mock_image(width=100, height=100):
    """Return a mock PIL image with fixed dimensions."""
    from unittest.mock import MagicMock
    img = MagicMock()
    img.width = width
    img.height = height
    return img


def test_extract_text_returns_string():
    with patch("services.ocr.Image.open", return_value=_mock_image()):
        with patch("services.ocr.pytesseract.image_to_string", return_value="Hello World"):
            result = extract_text("/fake/path.jpg")
    assert result == "Hello World"


def test_extract_text_returns_none_when_empty():
    with patch("services.ocr.Image.open", return_value=_mock_image()):
        with patch("services.ocr.pytesseract.image_to_string", return_value="   \n  "):
            result = extract_text("/fake/path.jpg")
    assert result is None


def test_extract_text_returns_none_on_error():
    with patch("services.ocr.Image.open", side_effect=Exception("tesseract not found")):
        result = extract_text("/fake/path.jpg")
    assert result is None
