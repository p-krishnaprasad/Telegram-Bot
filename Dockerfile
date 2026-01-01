# ---------- Base image ----------
FROM python:3.11-slim

# ---------- Environment ----------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------- Install system dependencies ----------
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ---------- Set working directory ----------
WORKDIR /app

# ---------- Install Python dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy application code ----------
COPY . .

# ---------- Expose port ----------
EXPOSE 5000

# ---------- Start app ----------
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "wsgi:app"]
