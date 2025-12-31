from app.utils import time_it
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL_NAME
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

SYSTEM_PROMPT = """
You are a receipt parsing engine.

Your task:
- Extract structured purchase data from OCR text.
- Return only valid JSON.
- Do not include explanations or extra text.
- Ignore totals, tax, and payment lines.
- Each purchased item must be its own array element.
- If price is missing, infer it from context if possible.

Output format (JSON):

{
  "seller": {
    "name": string,
    "address": string | null
  },
  "purchaseDate": "YYYY-MM-DD",
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
