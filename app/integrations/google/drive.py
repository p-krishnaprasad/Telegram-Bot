import random
import gspread
import io
from googleapiclient.http import MediaIoBaseUpload
from app.integrations.google.auth import get_drive_service
from app.components.utils import time_it
from datetime import datetime, timezone
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

@time_it
def get_expense_files(folder_id):
    drive = get_drive_service()

    query = (
        f"'{folder_id}' in parents "
        f"and name contains 'Expenses_' "
        f"and mimeType='application/vnd.google-apps.spreadsheet'"
    )

    results = drive.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()

    return results.get("files", [])

@time_it
def was_modified_today(spreadsheet_id):
    drive = get_drive_service()

    file = drive.files().get(
        fileId=spreadsheet_id,
        fields="modifiedTime"
    ).execute()

    modified_time = file["modifiedTime"]
    modified_dt = datetime.fromisoformat(
        modified_time.replace("Z", "+00:00")
    )

    today = datetime.now(timezone.utc).date()

    return modified_dt.date() == today