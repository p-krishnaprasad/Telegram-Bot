from flask import Blueprint, request, jsonify
import threading
from app.components.utils import print_process_flow_message
from app.flows.bot_manager import process_update

telegram_bp = Blueprint("telegram", __name__)

@telegram_bp.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    
    print_process_flow_message("🚀 Received Telegram Update")

    # Delegate the work to the service layer in a background thread
    threading.Thread(target=process_update, args=(data,)).start()
    
    return jsonify({"status": "ok"}), 200