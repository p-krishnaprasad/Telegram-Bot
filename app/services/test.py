"""
Manual test driver for sheets_manager.append_expenses

Run with:
    python tests/test_append_expenses.py
"""

from app.services.sheets_manager import append_expenses


def get_sample_expense_payload():
    return {
        "purchaseDate": "2026-01-08",
        "currency": "AUD",
        "seller": {
            "name": "Woolworths",
            "address": "123 George Street, Sydney"
        },
        "items": [
            {
                "itemName": "Milk 2L",
                "price": 4.50,
                "category": "Groceries"
            },
            {
                "itemName": "Bread",
                "price": 3.20,
                "category": "Groceries"
            }
        ]
    }


def main():
    print("Starting append_expenses test...")

    payload = get_sample_expense_payload()
    append_expenses(payload)

    print("✅ Test completed successfully")


if __name__ == "__main__":
    main()
