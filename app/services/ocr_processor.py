import pytesseract
from PIL import Image
import io

from app.utils import time_it

# Optional: for multi-language OCR, ensure Tesseract languages are installed
LANGUAGES = "eng+hin"  # add more as needed

@time_it
def extract_text_from_image(image_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img, lang=LANGUAGES)
        return text
    except Exception as e:
        print("OCR error:", e)
        return ""
