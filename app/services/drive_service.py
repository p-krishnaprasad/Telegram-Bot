import random
import gspread
import io
from googleapiclient.http import MediaIoBaseUpload
from app.services.google_auth import get_drive_service
from app.utils import time_it
from config import GOOGLE_DRIVE_IMAGES_FOLDER_ID

SPREADSHEET_MIME = "application/vnd.google-apps.spreadsheet"

drive_service = get_drive_service()

def find_spreadsheet(name):
    query = f"name='{name}' and mimeType='{SPREADSHEET_MIME}'"
    result = drive_service.files().list(q=query).execute()
    files = result.get("files", [])
    return files[0]["id"] if files else None

def find_worksheet_by_title(spreadsheet, title):
    try:
        worksheet = spreadsheet.worksheet(title)
        return worksheet
    except gspread.WorksheetNotFound:
        return None

@time_it
def upload_image_to_drive(
    image_bytes: bytes,
    cleaned_result: str
) -> str:
    """
    Upload image bytes to Google Drive folder using OAuth credentials.
    Returns Google Drive file ID.
    """
    seller_name = cleaned_result["seller"]["name"] or "unknown_seller"
    rand5 = random.randint(10000, 99999)

    filename = f"{seller_name}_{cleaned_result['purchaseDate']}_{rand5}.jpg"

    file_metadata = {
        "name": filename,
        "parents": [GOOGLE_DRIVE_IMAGES_FOLDER_ID],
    }

    media = MediaIoBaseUpload(
        io.BytesIO(image_bytes),
        mimetype="image/jpeg",
        resumable=False
    )

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()


    return file["id"], file["webViewLink"]