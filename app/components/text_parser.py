import csv
from io import StringIO

def parse_text_expense(message_text):
    """
    Flexible CSV-style expense parser.
    Required: date, item, price, category
    Optional: currency (default AUD), seller, seller address
    """
    reader = csv.reader(StringIO(message_text))
    row = next(reader)

    if len(row) < 4:
        raise ValueError("Minimum required fields: date, item, price, category")

    date = row[0].strip()
    item = row[1].strip()
    price = float(row[2])

    currency = row[3].strip() if len(row) > 3 and row[3].strip() else "AUD"
    category = row[4].strip() if len(row) > 4 else None

    seller = row[5].strip() if len(row) > 5 else None
    seller_address = row[6].strip() if len(row) > 6 else None

    return {
        "seller": {
            "name": seller,
            "address": seller_address
        },
        "receipt_link": None,
        "purchaseDate": date,
        "currency": currency,
        "items": [
            {
                "itemName": item,
                "price": price,
                "category": category
            }
        ]
    }
