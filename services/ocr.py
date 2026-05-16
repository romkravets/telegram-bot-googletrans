import logging
from typing import Optional
import pytesseract
from PIL import Image


def extract_text(image_path: str) -> Optional[str]:
    try:
        img = Image.open(image_path)
        if img.width * img.height > 4_000 * 4_000:
            img = img.resize((2000, 2000), Image.LANCZOS)
        text = pytesseract.image_to_string(img).strip()
        return text if text else None
    except Exception as e:
        logging.warning("OCR failed for %s: %s", image_path, e)
        return None
