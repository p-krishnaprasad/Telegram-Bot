import io
from PIL import Image
import pytesseract
from app.components.utils import time_it

# Optional: for multi-language OCR, ensure Tesseract languages are installed
LANGUAGES = "eng"  # add more as needed


# -----------------------------
# Helper: Local Tesseract OCR
# -----------------------------
def local_ocr(image_bytes: bytes) -> str:
    """Fallback OCR using local Tesseract."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img, lang=LANGUAGES)
        return text
    except Exception as e:
        print("OCR error:", e)
        return ""

# -----------------------------
# Main OCR function with failover
# -----------------------------
@time_it
def extract_text_from_image(image_bytes: bytes) -> str:
    # Fallback to local OCR
    try:
        text = local_ocr(image_bytes)
        print("✅ Local Tesseract succeeded")
        return text
    except Exception as e:
        print(f"❌ Local Tesseract failed: {e}")
        return ""