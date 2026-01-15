import json
from app.services.telegram_service import download_telegram_file, send_reply
from app.services.ocr_processor import extract_text_from_image
from app.services.ai_parser import ai_ocr_parser
from app.services.text_parser import parse_text_expense
from app.services.sheets_manager import append_expenses
from app.utils import time_it
from config import ENABLE_LOGS

PROCESSED_UPDATES = set()

@time_it
def process_update(data):
    """
    Orchestrator:
    - Photo → OCR → AI → Sheets
    - Text  → Direct Parse → Sheets
    """
    try:
        update_id = data.get("update_id")
        if not update_id or update_id in PROCESSED_UPDATES:
            return
        PROCESSED_UPDATES.add(update_id)
        print(f"Processing update_id: {update_id}")
        message = data.get("message")
        if not message:
            return

        chat_id = message["chat"]["id"]

        # ---------------------------------
        # 📝 TEXT MESSAGE FLOW
        # ---------------------------------
        if "text" in message:
            try:
                parsed_result = parse_text_expense(message["text"])
                append_expenses(parsed_result)
                send_reply(chat_id, parsed_result)
            except Exception as e:
                send_reply(
                    chat_id,
                    "❌ Invalid format.\n"
                    'Expected:\n"date","item","price","AUD","Category","Seller","Seller Address"'
                )
            return

        # ---------------------------------
        # 📷 PHOTO MESSAGE FLOW
        # ---------------------------------
        if "photo" in message:
            file_id = message["photo"][-1]["file_id"]

            img_bytes = download_telegram_file(file_id)
            if not img_bytes:
                send_reply(chat_id, "❌ Failed to download image.")
                return

            ocr_text = extract_text_from_image(img_bytes)
            if not ocr_text:
                send_reply(chat_id, "❌ No text detected in image.")
                return
            if ENABLE_LOGS == "true":
                print(f"OCR Extracted Text: {ocr_text}")

            parsed_result = ai_ocr_parser(ocr_text)

            if ENABLE_LOGS == "true":
                print(f"AI Parsed Result: {parsed_result}")
            cleaned_result = json.loads(
                parsed_result.strip()
                .replace("```json", "")
                .replace("```", "")
            )

            append_expenses(cleaned_result)
            send_reply(chat_id, cleaned_result)
            return

        # ---------------------------------
        # Unsupported message
        # ---------------------------------
        send_reply(chat_id, "⚠️ Please send a photo or formatted text.")

    except Exception as e:
        print(f"Orchestration Error: {e}")
