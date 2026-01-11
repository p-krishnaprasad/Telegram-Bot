# 📄 Receipt2Sheets — AI-Powered Telegram Expense Tracker

Receipt2Sheets is a **Telegram bot** that automatically reads expense receipts (images or text), extracts structured data using **OCR + AI**, and appends the results into **Google Sheets**.

The application is deployed on **Render**, uses **OpenRouter** for AI parsing, and integrates with **Google Drive & Google Sheets** using OAuth credentials.

---

## 🏗️ High-Level Architecture

![Receipt2Sheets Architecture](https://raw.githubusercontent.com/p-krishnaprasad/Image-host/refs/heads/main/Portfolio/Receipt2Sheets.png)

---

## 🚀 Features

- 📸 Receipt image processing using OCR
- 📝 Text-based expense parsing
- 🤖 AI-powered semantic extraction via OpenRouter
- 📊 Automatic Google Sheets append
- 📁 Files stored in a specific Google Drive folder
- ⚡ Fast Telegram response with background processing
- 🔁 Duplicate Telegram update protection
- ☁️ Cloud-native deployment on Render

---

## 🧰 Tech Stack

- **Python 3.11**
- **Flask**
- **Telegram Bot API**
- **Tesseract OCR**
- **OpenRouter (LLM API)**
- **Google Drive API**
- **Google Sheets API**
- **Gunicorn**
- **Docker**
- **Render**

---

## 🔑 Prerequisites

### 1️⃣ Telegram Bot

- Create a bot via **@BotFather**
- Save the **BOT_TOKEN**

---

### 2️⃣ OpenRouter (LLM Provider)

- Create an account at https://openrouter.ai
- Generate an API key
- Choose a supported model (example: `openai/gpt-4o-mini`)

---

### 3️⃣ Google OAuth Credentials (Drive + Sheets)

This project uses **OAuth (Client ID + Refresh Token)** instead of a service account.

Steps:

1. Create a project in **Google Cloud Console**
2. Enable:
   - Google Drive API
   - Google Sheets API
3. Create **OAuth Client ID**
4. Generate:
   - Client ID
   - Client Secret
   - Refresh Token
5. Create a target folder in Google Drive and note its **Folder ID**

---

## ⚙️ Environment Variables (Render)

Set the following variables in **Render → Service → Environment**:

```env
BOT_TOKEN=your_telegram_bot_token

OPENROUTER_MODEL_NAME=openai/gpt-4o-mini
OPENROUTER_API_KEY=your_openrouter_api_key

GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REFRESH_TOKEN=your_google_refresh_token
⚠️ Do NOT commit secrets to GitHub.
All secrets should live in Render Environment Variables.
```

---

🧪 Local Development

1️⃣ Clone repository
bash
Copy code
git clone https://github.com/yourusername/receipt2sheets.git
cd receipt2sheets
2️⃣ Create virtual environment
bash
Copy code
python -m venv venv
source venv/bin/activate
3️⃣ Install system dependencies (Linux / WSL)
bash
Copy code
sudo apt update
sudo apt install -y tesseract-ocr poppler-utils
4️⃣ Install Python dependencies
bash
Copy code
pip install -r requirements.txt
▶️ Run Locally
bash
Copy code
gunicorn -w 1 -b 0.0.0.0:5000 wsgi:app
☁️ Deployment on Render
1️⃣ Create a new Web Service
Runtime: Docker

Region: Any

Branch: main

2️⃣ Build Command
nginx
Copy code
docker build -t receipt2sheets .
3️⃣ Start Command
nginx
Copy code
gunicorn -w 1 -b 0.0.0.0:5000 wsgi:app
🔗 Telegram Webhook Setup
After Render deployment, set webhook:

bash
Copy code
curl -X POST \
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook \
-d "url=https://your-render-app.onrender.com/telegram"
Verify webhook:

bash
Copy code
curl https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo

---

🛡️ Reliability & Safety
Prevents duplicate Telegram update_id processing

Acknowledges Telegram quickly to avoid retries

Isolates OCR, AI, and Sheets logic into services

Timing and performance logging built-in

---

📈 Future Improvements
Monthly expense summaries

Charts & dashboards

Multi-currency support

PDF receipt support

Google Drive receipt archiving

---

🧑‍💻 Author
Krishna Prasad
Senior Software Engineer
AI Automation • Cloud • Backend Systems

---

📜 License
MIT License

```

```
