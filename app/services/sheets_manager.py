import gspread
from dateutil import parser
from app.services.google_auth import (
    get_gspread_client,
    get_drive_service
)
from app.services.drive_service import (
    find_spreadsheet
)
from app.utils import time_it
from config import GOOGLE_DRIVE_FOLDER_ID
import time

gc = get_gspread_client()
drive_service = get_drive_service()

YEARLY_FILE_PREFIX = "Expenses_"

MONTH_SHEETS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

HEADERS = [
    "date",
    "item",
    "price",
    "currency",
    "category",
    "seller",
    "seller address"
]

# -----------------------------
# HELPERS
# -----------------------------
def get_year_and_month(purchase_date: str):
    dt = parser.parse(purchase_date)
    return (
        dt.year,
        MONTH_SHEETS[dt.month - 1],
        dt.strftime("%Y-%m-%d")
    )

def format_header(worksheet, headers):
    # Insert header row (1 write)
    worksheet.insert_row(headers, 1)

    # Batch all formatting into ONE request
    worksheet.batch_format([
        {
            "range": "A1:G1",
            "format": {
                "backgroundColor": {
                    "red": 0,
                    "green": 0,
                    "blue": 0
                },
                "horizontalAlignment": "CENTER",
                "textFormat": {
                    "bold": True,
                    "foregroundColor": {
                        "red": 1,
                        "green": 1,
                        "blue": 1
                    },
                    "fontSize": 11
                }
            }
        }
    ])

    # Freeze + filter (2 writes, unavoidable)
    worksheet.freeze(rows=1)

def create_yearly_expense_sheet(sheet_name, parent_folder_id):
    spreadsheet = gc.create(sheet_name, folder_id=parent_folder_id)

    # Rename default sheet to Jan
    spreadsheet.sheet1.update_title(MONTH_SHEETS[0])

    # Add remaining months
    for month in MONTH_SHEETS[1:]:
        spreadsheet.add_worksheet(
            title=month,
            rows=1000,
            cols=len(HEADERS)
        )

    # Headers & formatting
    for month in MONTH_SHEETS:
        ws = spreadsheet.worksheet(month)
        if not ws.row_values(1): #to reserver the spot for headers and avoid overwriting headers with data
            format_header(ws, HEADERS)

    return spreadsheet.id


def get_or_create_yearly_sheet(year: int):
    file_name = f"{YEARLY_FILE_PREFIX}{year}"
    existing_sheet = find_spreadsheet(drive_service, file_name)
    if existing_sheet:
        return gc.open_by_key(existing_sheet["id"])

    # new_file_id = create_yearly_expense_sheet(file_name, parent_folder_id)
    new_file = create_yearly_expense_sheet(file_name, GOOGLE_DRIVE_FOLDER_ID)

    return gc.open_by_key(new_file)


# -----------------------------
# MAIN ENTRY POINT
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
        raise RuntimeError(f"Worksheet '{month_sheet}' not found")
    
    if not worksheet.row_values(1):
        format_header(worksheet, HEADERS)

    rows = [
        [
            formatted_date,
            item["itemName"],
            item["price"],
            data["currency"],
            item["category"],
            data["seller"]["name"],
            data["seller"]["address"]
        ]
        for item in data["items"]
    ]

    worksheet.append_rows(rows, value_input_option="USER_ENTERED")
