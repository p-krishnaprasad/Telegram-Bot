import gspread
from dateutil import parser
from app.services.google_auth import (
    get_gspread_client
)
from app.services.drive_service import (
    find_spreadsheet,
    find_worksheet_by_title
)
from app.utils import time_it
from config import GOOGLE_DRIVE_SHEETS_FOLDER_ID

gc = get_gspread_client()

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
    "seller address",
    "receipt_link"
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
            "range": "A1:H1",
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

def create_worksheet_with_headers(spreadsheet, title):
    ws = spreadsheet.add_worksheet(
        title=title,
        rows=1000,
        cols=len(HEADERS)
    )
    if not ws.row_values(1): #to reserve the spot for headers and avoid overwriting headers with data
        format_header(ws, HEADERS)

    return spreadsheet.id

def create_sheet(sheet_name, title, parent_folder_id):
    spreadsheet = gc.create(sheet_name, folder_id=parent_folder_id)

    create_worksheet_with_headers(spreadsheet, title)
    
    # Delete default Sheet1
    spreadsheet.del_worksheet(spreadsheet.sheet1)

    return spreadsheet.id


def get_or_create_yearly_sheet(year: int, title: str):
    file_name = f"{YEARLY_FILE_PREFIX}{year}"
    existing_sheet = find_spreadsheet(file_name)
    if existing_sheet:
        spreadsheet = gc.open_by_key(existing_sheet)  # Preload to avoid multiple opens
        if find_worksheet_by_title(spreadsheet,
            title
        ) == None:
            create_worksheet_with_headers(spreadsheet, title)
            
        return spreadsheet
    # Create new yearly sheet
    new_file = create_sheet(file_name, title, GOOGLE_DRIVE_SHEETS_FOLDER_ID)

    return gc.open_by_key(new_file)


# -----------------------------
# MAIN ENTRY POINT
# -----------------------------
@time_it
def append_expenses(data: dict):
    year, month_sheet, formatted_date = get_year_and_month(
        data["purchaseDate"]
    )

    spreadsheet = get_or_create_yearly_sheet(year, month_sheet)
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
            data["seller"]["name"] if idx == 0 else "",  # Only include seller name for the first item
            data["seller"]["address"] if idx == 0 else "",  # Only include seller address for the first item
            data["receipt_link"] if idx == 0 else ""  # Only include receipt link for the first item
        ]
        for idx, item in enumerate(data["items"])
    ]

    worksheet.append_rows(rows, value_input_option="USER_ENTERED")
