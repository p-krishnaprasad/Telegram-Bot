import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from dateutil import parser
from app.utils import time_it
from config import GSHEET_CREDS_JSON
# -----------------------------
# CONFIG
# -----------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

TEMPLATE_FILE_NAME = "Expenses_Template"
YEARLY_FILE_PREFIX = "Expenses_"

MONTH_SHEETS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

# -----------------------------
# AUTH
# -----------------------------
credentials = Credentials.from_service_account_file(
    GSHEET_CREDS_JSON, scopes=SCOPES
)

gc = gspread.authorize(credentials)
drive_service = build("drive", "v3", credentials=credentials)

# -----------------------------
# HELPERS
# -----------------------------
def get_year_and_month(purchase_date: str):
    dt = parser.parse(purchase_date)
    year = dt.year
    month_sheet = MONTH_SHEETS[dt.month - 1]
    return year, month_sheet, dt.strftime("%Y-%m-%d")


def find_drive_file(file_name):
    query = f"name='{file_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query).execute()
    files = results.get("files", [])
    return files[0] if files else None

def get_template_parent_folder_id(template_file_id):
    file = drive_service.files().get(
        fileId=template_file_id,
        fields="parents",
        supportsAllDrives=True
    ).execute()

    parents = file.get("parents", [])
    if not parents:
        raise Exception("Template file has no parent folder")

    return parents[0]

def copy_template(new_file_name):
    template = find_drive_file(TEMPLATE_FILE_NAME)
    if not template:
        raise Exception("Expenses_Template not found in Drive")

    parent_folder_id = get_template_parent_folder_id(template["id"])

    copied = drive_service.files().copy(
        fileId=template["id"],
        body={
            "name": new_file_name,
            "parents": [parent_folder_id]
        },
        supportsAllDrives=True
    ).execute()

    return copied["id"]



def get_or_create_yearly_sheet(year: int):
    file_name = f"{YEARLY_FILE_PREFIX}{year}"
    file = find_drive_file(file_name)
    if file:
        return gc.open(file_name)

    # Create from template
    new_file_id = copy_template(file_name)
    return gc.open_by_key(new_file_id)

# -----------------------------
# MAIN FUNCTION
# -----------------------------
@time_it
def append_expenses(data: dict):
    year, month_sheet, formatted_date = get_year_and_month(
        data["purchaseDate"]
    )

    spreadsheet = get_or_create_yearly_sheet(year)

    try:
        worksheet = spreadsheet.worksheet(month_sheet)
    except gspread.WorksheetNotFound:
        raise Exception(f"Worksheet '{month_sheet}' not found")

    rows = []
    for item in data["items"]:
        rows.append([
            formatted_date,
            item["itemName"],
            item["price"],
            data["currency"],
            item["category"],
            data["seller"]["name"],
            data["seller"]["address"]
        ])

    worksheet.append_rows(rows, value_input_option="USER_ENTERED")
