import json
from app.services.telegram_service import download_telegram_file, send_reply
from app.services.ocr_processor import extract_text_from_image
from app.services.ai_parser import ai_ocr_parser
from app.services.sheets_manager import append_expenses
from app.utils import time_it

# Keep deduplication at the manager level
PROCESSED_UPDATES = set()

@time_it
def process_update(data):
    """
    The Orchestrator: Connects Telegram -> OCR -> AI Parser
    """
    try:
        # 1. Telegram Service: Validation & Deduplication
        update_id = data.get("update_id")
        if not update_id or update_id in PROCESSED_UPDATES:
            return
        PROCESSED_UPDATES.add(update_id)

        if "message" not in data or "photo" not in data["message"]:
            return

        chat_id = data["message"]["chat"]["id"]
        file_id = data["message"]["photo"][-1]["file_id"]

        # 2. Telegram Service: Download
        # We move the complexity of requests/getFile into its own service
        img_bytes = download_telegram_file(file_id)
        if not img_bytes:
            send_reply(chat_id, "Sorry, I couldn't download the image.")
            return

        # 3. OCR Service: Extract Text
        ocr_text = extract_text_from_image(img_bytes)
        if not ocr_text:
            send_reply(chat_id, "I couldn't find any text in that photo.")
            return
        # print(f"OCR Extracted Text: {ocr_text}")

        # 4. AI Parser Service: Structure the data
        parsed_result = ai_ocr_parser(ocr_text)
        cleaned_result = json.loads(parsed_result.strip().replace("```json", "").replace("```", ""))

        # 5. Upload to Google Sheets
        append_expenses(cleaned_result)

        # 6. Final Output
        send_reply(chat_id, cleaned_result)

    except Exception as e:
        print(f"Orchestration Error: {e}")