from app.components.utils import time_it
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL_NAME
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

SYSTEM_PROMPT = """
You are a strict receipt parsing engine.

Your task:
- Extract structured purchase data from OCR text.
- Return only valid JSON.
- Do NOT include explanations, markdown, comments, or extra text.

GENERAL RULES:
- Ignore totals, tax, payment methods, invoice numbers, ABN, phone numbers, and register metadata.
- Each purchased product must be represented as ONE item in the items array.
- If an item has a quantity format like “X @ price = total”, use the TOTAL price.
- Normalize multi-line item descriptions into a single itemName string.
- Do NOT invent items or prices.
- If a price is missing, infer it ONLY if clearly derivable from quantity × unit price.

SELLER:
- seller.name should be the main store brand (short name preferred).
- seller.address should be the store location if present, otherwise null.

DATE & TIME:
- Extract purchase date and time if present.
- Convert to ISO format: YYYY-MM-DD HH:MM:SS
- If time is missing, default to 00:00:00
- if date is missing, use today's date

QUANTITY & PRICING RULES:
- If an item uses a quantity format like “X @ unit_price = total_price”:
- Use the TOTAL price as the item price.
- Preserve the quantity and unit price text (e.g., “6 @ $5.00”) inside the itemName.
- Do NOT expand quantities into multiple items.

Output format (JSON):

{
  "seller": {
    "name": string,
    "address": string | null
  },
  "purchaseDate": "YYYY-MM-DD HH:MM:SS",
  "currency": "AUD",
  "items": [
    {
      "itemName": string,
      "price": number,
      "category": one of [
        "Grocery",
        "Food",
        "Electronics",
        "Clothing",
        "Household",
        "Personal",
        "Transport",
        "Tools",
        "Entertainment",
        "Other"
      ]
    }
  ]
}
"""

@time_it
def ai_ocr_parser(ocr_text: str) -> str:
    try:
        # API call using the official SDK
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ocr_text}
            ],
            temperature=0,
            # If your model supports reasoning (like the example you shared):
            # extra_body={"reasoning": {"enabled": True}} 
        )

        # The SDK automatically converts the JSON into an object
        # You access fields with dot notation: .choices[0].message.content
        output_text = response.choices[0].message.content
        return output_text

    except Exception as e:
        print(f"OCR error: {e}")
        return ""
