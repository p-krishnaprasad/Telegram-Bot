from flask import Blueprint, request, jsonify
import threading
from app.services.bot_manager import process_update

telegram_bp = Blueprint("telegram", __name__)

@telegram_bp.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    
    print(f"Received update")

    # Delegate the work to the service layer in a background thread
    threading.Thread(target=process_update, args=(data,)).start()
    
    return jsonify({"status": "ok"}), 200