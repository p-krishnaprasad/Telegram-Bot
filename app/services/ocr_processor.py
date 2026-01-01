import base64
import io
from PIL import Image
import pytesseract
import requests
from app.utils import time_it
from config import OCR_SPACE_API_KEY

# -----------------------------
# CONFIG
# -----------------------------
OCR_SPACE_URL = "https://api.ocr.space/parse/image"

# Optional: for multi-language OCR, ensure Tesseract languages are installed
LANGUAGES = "eng"  # add more as needed
# -----------------------------
# Helper: OCR.Space
# -----------------------------
def ocr_space(image_bytes: bytes) -> str:
    """
    Send image bytes to OCR.Space using base64 format.
    Returns extracted text.
    """
    # Encode bytes to base64 string
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    base64_image = f"data:image/jpeg;base64,{base64_str}"

    # Prepare payload
    data = {
        "apikey": OCR_SPACE_API_KEY,
        "base64Image": base64_image,
        "language": LANGUAGES,
        "isOverlayRequired": False
    }

    try:
        response = requests.post(OCR_SPACE_URL, data=data, timeout=60)
        response.raise_for_status()
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            error = result.get("ErrorMessage", "Unknown OCR error")
            raise RuntimeError(f"OCR.Space error: {error}")

        parsed_results = result.get("ParsedResults")
        if not parsed_results:
            return ""

        return parsed_results[0].get("ParsedText", "").strip()

    except Exception as e:
        print(f"⚠️ OCR.Space request failed: {e}")
        return ""

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
    """
    Try OCR.Space first, fallback to local Tesseract if online fails.
    Returns extracted text as string.
    """
    try:
        text = ocr_space(image_bytes)
        if text.strip():
            print("✅ OCR.Space succeeded")
            return text
        else:
            print("⚠️ OCR.Space returned empty text, using local Tesseract")
    except Exception as e:
        print(f"⚠️ OCR.Space failed: {e}")

    # Fallback to local OCR
    try:
        text = local_ocr(image_bytes)
        print("✅ Local Tesseract succeeded")
        return text
    except Exception as e:
        print(f"❌ Local Tesseract failed: {e}")
        return ""
