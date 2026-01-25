import requests
from app.services.sheets_manager import MONTH_SHEETS
from app.utils import time_it
from config import BOT_TOKEN
from dateutil import parser


# Base URLs for Telegram API
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{BOT_TOKEN}"

@time_it
def download_telegram_file(file_id: str) -> bytes:
    """
    Handles the two-step process of getting a file path and downloading the content.
    """
    try:
        # Step 1: Get the file path from Telegram
        file_info_resp = requests.get(
            f"{TELEGRAM_API}/getFile", 
            params={"file_id": file_id}, 
            timeout=60
        )
        file_info_resp.raise_for_status()
        file_path = file_info_resp.json().get("result", {}).get("file_path")

        if not file_path:
            print(f"Error: No file_path returned for {file_id}")
            return None

        # Step 2: Download the actual image bytes
        download_url = f"{FILE_API}/{file_path}"
        img_resp = requests.get(download_url, timeout=15)
        img_resp.raise_for_status()

        return img_resp.content

    except requests.exceptions.RequestException as e:
        print(f"Telegram Download Error: {e}")
        return None

@time_it
def send_reply(chat_id: int, parsed_result: dict = {}, message: str = None):
    """
    Sends a text message back to the Telegram user.
    """
    if message:
        response_msg = message
    else:
        purchase_date = parsed_result.get("purchaseDate", "2025-12-31")
        dt = parser.parse(purchase_date)
        year = dt.year
        month_sheet = MONTH_SHEETS[dt.month - 1]
        file_name = f"Expenses_{year}"
        sheet_name = month_sheet
        items = parsed_result.get("items", [])
        item_count = len(items)

        if items:
            # Building a fancy multiline message
            response_msg = (
                f"✅ *Processing Complete*\n\n"
                f"📊 **Items Added:** `{item_count}`\n"
                f"📄 **Source File:** `{file_name}`\n"
                f"📒 **Google Sheet:** `{sheet_name}`\n\n"
                f"✨ _Data has been synced successfully!_"
        )
        else:
            response_msg = (
                "⚠️ *OCR Finished*\n"
                "I processed the image, but I couldn't find any line items to add. "
                "Please make sure the receipt is clear and well-lit."
            )
    try:
        payload = {
            "chat_id": chat_id,
            "text": response_msg,
            "parse_mode": "Markdown"  # Allows for bold/italic formatting
        }
        response = requests.post(
            f"{TELEGRAM_API}/sendMessage", 
            data=payload, 
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Telegram Send Error: {e}")