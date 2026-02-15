import requests
from app.components.utils import print_summary_result, time_it
from app.integrations.google.auth import get_sheets_service
from app.integrations.google.sheets import analyze_sheet
from app.integrations.google.drive import get_expense_files, was_modified_today
from config import GOOGLE_DRIVE_SHEETS_FOLDER_ID

@time_it
def rebuild_summary(spreadsheet_id):
    service = get_sheets_service()
    
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()
    
    raw_sheets = spreadsheet["sheets"]
    
    sheets = []
    summary_sheet = None
    
    # 🔹 Single loop to build sheets list and capture Summary
    for sheet in raw_sheets:
        props = sheet["properties"]
    
        sheet_info = {
            "title": props["title"],
            "sheetId": props["sheetId"]
        }
    
        sheets.append(sheet_info)
    
        if props["title"] == "Summary":
            summary_sheet = sheet
    
    # 🔹 Get Summary sheetId
    dashboard_id = summary_sheet["properties"]["sheetId"]
    
    requests = []
    
    # 🔹 1️⃣ Delete existing charts from Summary
    for chart in summary_sheet.get("charts", []):
        requests.append({
            "deleteEmbeddedObject": {
                "objectId": chart["chartId"]
            }
        })
    
    # 🔹 2️⃣ Clear Summary sheet grid
    requests.append({
        "updateCells": {
            "range": {
                "sheetId": dashboard_id
            },
            "fields": "*"
        }
    })
    
    chart_row_position = 0

    for sheet in sheets:

        if sheet["title"] == "Summary":
            continue

        source_sheet_id = sheet["sheetId"]

        pivot_start_row = chart_row_position
        total_price, category_count, last_row = analyze_sheet(spreadsheet_id, sheet["title"])

        pivot_end_row = pivot_start_row + category_count
        # Create Pivot
        requests.append({
            "updateCells": {
                "rows": [{
                    "values": [{
                        "pivotTable": {
                            "source": {
                                "sheetId": source_sheet_id,
                                "startRowIndex": 0, 
                                "endRowIndex": last_row,
                                "startColumnIndex": 0,
                                "endColumnIndex": 8
                            },
                            "rows": [{
                                "sourceColumnOffset": 4,
                                "showTotals": True,
                                "sortOrder": "ASCENDING"
                            }],
                            "values": [{
                                "summarizeFunction": "SUM",
                                "sourceColumnOffset": 2,
                                "name": "Total Price"
                            }]
                        }
                    }]
                }],
                "start": {
                    "sheetId": dashboard_id,
                    "rowIndex": pivot_start_row,
                    "columnIndex": 0
                },
                "fields": "pivotTable"
            }
        })

        # Create Donut Chart
        requests.append({
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": f"{sheet['title']} - ${total_price}",
                            "pieChart": {
                                "legendPosition": "RIGHT_LEGEND",
                                "pieHole": 0.4,
                                "domain": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": dashboard_id,
                                            "startRowIndex": pivot_start_row,
                                            "endRowIndex": pivot_end_row,
                                            "startColumnIndex": 0,
                                            "endColumnIndex": 1
                                        }]
                                    }
                                },
                                "series": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": dashboard_id,
                                            "startRowIndex": pivot_start_row,
                                            "endRowIndex": pivot_end_row,
                                            "startColumnIndex": 1,
                                            "endColumnIndex": 2
                                        }]
                                    }
                                }
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": dashboard_id,
                                    "rowIndex": pivot_start_row,
                                    "columnIndex": 4
                                }
                            }
                        }
                    }
                }
            })


        chart_row_position += 25

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()

@time_it
def summarise_expense_sheets():
    files = get_expense_files(GOOGLE_DRIVE_SHEETS_FOLDER_ID)

    processed = []
    skipped = []

    for file in files:
        spreadsheet_id = file["id"]
        name = file["name"]

        if was_modified_today(spreadsheet_id):
            # print(f"{name} modified today. Rebuilding summary.")
            rebuild_summary(spreadsheet_id)
            # print(f"Summary rebuilt for {name}")
            processed.append(name)
        else:
            # print(f"{name} not modified today. Skipping.")
            skipped.append(name)
    
    print_summary_result(processed, skipped, len(files))
