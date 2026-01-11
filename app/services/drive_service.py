SPREADSHEET_MIME = "application/vnd.google-apps.spreadsheet"

def find_spreadsheet(drive_service, name):
    query = f"name='{name}' and mimeType='{SPREADSHEET_MIME}'"
    result = drive_service.files().list(q=query).execute()
    files = result.get("files", [])
    return files[0] if files else None


def get_parent_folder_id(drive_service, file_id):
    file = drive_service.files().get(
        fileId=file_id,
        fields="parents",
        supportsAllDrives=True
    ).execute()

    parents = file.get("parents", [])
    if not parents:
        raise RuntimeError("File has no parent folder")

    return parents[0]
