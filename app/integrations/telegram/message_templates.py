class TelegramMessages:
    UNAUTHORIZED_USER = (
        "🔒 *Access Restricted*\n\n"
        "Sorry, you don’t have permission to use this bot.\n"
    )

    TEXT_FORMAT_ERROR = (
        "❌ *Invalid format detected*\n\n"
        "📌 *Expected input format:*\n"
        "`\"date\",\"item\",\"price\",\"AUD\",\"Category\",\"Seller\",\"Seller Address\"`\n\n"
        "🧩 *Minimum required fields:*\n"
        "• `date`\n"
        "• `item`\n"
        "• `price`\n"
        "• `category`\n\n"
        "💡 _Tip:_ You can omit optional fields like currency, seller, or address."
    )

    IMAGE_DOWNLOAD_ERROR = (
        "🚫 *Image download failed*\n\n"
        "I ran into an issue while accessing the photo.\n"
        "Kindly resend the image to continue 📸"
    )

    NO_TEXT_IN_IMG = (
        "🔍 *No readable text found*\n\n"
        "I processed the image, but couldn’t detect any readable text.\n"
        "Make sure the receipt is:\n"
        "• well-lit\n"
        "• clearly focused\n"
        "• fully visible"
    )

    UNSUPPORTED_MESSAGE = (
        "⚠️ *Unsupported message type*\n\n"
        "Please send:\n"
        "• a receipt photo 📸\n"
        "• or a properly formatted expense text 📝"
    )
