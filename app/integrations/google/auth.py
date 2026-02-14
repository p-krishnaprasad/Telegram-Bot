import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REFRESH_TOKEN
)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_credentials():
    return Credentials(
        token=None,
        refresh_token=GOOGLE_REFRESH_TOKEN,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )


def get_gspread_client():
    creds = get_credentials()
    return gspread.authorize(creds)

def get_sheets_service():
    return build("sheets", "v4", credentials=get_credentials())

def get_drive_service():
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)
