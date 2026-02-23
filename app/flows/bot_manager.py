from datetime import date
import json
from app.integrations.google.drive import upload_image_to_drive
from app.integrations.telegram.webhook import download_telegram_file, send_reply
from app.integrations.ocr_processor import extract_text_from_image
from app.integrations.ai_parser import ai_ocr_parser
from app.components.text_parser import parse_text_expense
from app.integrations.google.sheets import append_expenses
from app.components.utils import time_it
from config import ENABLE_LOGS, SAVE_RECEIPT, TELEGRAM_ALLOWED_USERS
from app.integrations.telegram.message_templates import TelegramMessages as TM

PROCESSED_UPDATES = set()

@time_it
def process_update(data):
    """
    Orchestrator:
    - Photo → OCR → AI → Sheets
    - Text  → Direct Parse → Sheets
    """
    user_id = data.get("message", {}).get("from", {}).get("id")
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    if user_id not in TELEGRAM_ALLOWED_USERS:
        send_reply(
                    chat_id,
                    message=TM.UNAUTHORIZED_USER
                )
        return

    try:
        update_id = data.get("update_id")
        if not update_id or update_id in PROCESSED_UPDATES:
            return
        PROCESSED_UPDATES.add(update_id)
        print(f"Processing update_id: {update_id}")
        message = data.get("message")
        if not message:
            return
        
        # ---------------------------------
        # 📝 TEXT MESSAGE FLOW
        # ---------------------------------
        if "text" in message:
            process_expense(
                chat_id=chat_id,
                raw_text=message["text"],
                receipt_link=message["text"],  # store original text
            )
            return

        # ---------------------------------
        # 📷 PHOTO MESSAGE FLOW
        # ---------------------------------
        if "photo" in message:
            file_id = message["photo"][-1]["file_id"]

            img_bytes = download_telegram_file(file_id)
            if not img_bytes:
                send_reply(chat_id, message=TM.IMAGE_DOWNLOAD_ERROR)
                return

            ocr_text = extract_text_from_image(img_bytes)
            if not ocr_text:
                send_reply(chat_id, message=TM.NO_TEXT_IN_IMG)
                return

            if ENABLE_LOGS == "true":
                print(f"OCR Extracted Text: {ocr_text}")

            process_expense(
                chat_id=chat_id,
                raw_text=ocr_text,
                img_bytes=img_bytes
            )
            return

        # ---------------------------------
        # Unsupported message
        # ---------------------------------
        send_reply(chat_id, message=TM.UNSUPPORTED_MESSAGE)

    except Exception as e:
        print(f"Orchestration Error: {e}")


def process_expense(chat_id, raw_text, receipt_link=None, img_bytes=None):
    try:
        # Add system date
        raw_text += f"\n\nsystem_date: {date.today()}"

        parsed_result = ai_ocr_parser(raw_text)

        if ENABLE_LOGS == "true":
            print(f"AI Parsed Result: {parsed_result}")

        cleaned_result = json.loads(
            parsed_result.strip()
            .replace("```json", "")
            .replace("```", "")
        )

        # Upload image if required
        if img_bytes and SAVE_RECEIPT == "true":
            _, receipt_link = upload_image_to_drive(
                img_bytes,
                cleaned_result,
            )

        cleaned_result["receipt_link"] = receipt_link

        append_expenses(cleaned_result)

        send_reply(chat_id, cleaned_result)

    except Exception:
        send_reply(chat_id, message=TM.TEXT_FORMAT_ERROR)