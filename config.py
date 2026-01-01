import os
from dotenv import load_dotenv

load_dotenv()
# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# OCR.Space
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "helloworld")

# Google Sheets
GOOGLE_SERVICE_ACCOUNT = os.getenv("GOOGLE_SERVICE_ACCOUNT", "")

#Openrouter
OPENROUTER_MODEL_NAME = os.getenv("OPENROUTER_MODEL_NAME", "YOUR_OPENROUTER_MODEL_NAME")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")