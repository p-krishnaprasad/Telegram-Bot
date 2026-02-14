import threading
from flask import Blueprint, jsonify
from app.components.utils import print_process_flow_message
from app.flows.summary_manager import summarise_expense_sheets

summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/summary", methods=["GET"])
def summary():

    print_process_flow_message("📊  Summary Generation Triggered")

    threading.Thread(target=summarise_expense_sheets, args=()).start()
    
    return jsonify({"status": "ok"}), 200
