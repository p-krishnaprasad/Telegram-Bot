from google_auth_oauthlib.flow import InstalledAppFlow
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
CLIENT_CONFIG = {
    "installed": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]

flow = InstalledAppFlow.from_client_config(
    CLIENT_CONFIG,
    SCOPES
)

creds = flow.run_local_server(port=8080)

print("REFRESH TOKEN:", creds.refresh_token)
