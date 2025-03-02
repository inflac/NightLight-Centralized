from flask import Blueprint, jsonify, request
from app.models import Nightline

nightline_bp = Blueprint("nightline", __name__)

# Route to update the status of a nightline
@nightline_bp.route("/<string:name>/status", methods=["PATCH"])
def update_status(name):
    """Set the status of a nightline."""
    nightline = Nightline.get_nightline(name)

    data = request.get_json()
    if not data or "status" not in data:
        raise ValueError(f"Status not found in data")

    nightline.set_status(data["status"])

    return jsonify({
        "status": nightline.status
    }), 200

# Route to update the 'now' boolean of a nightline
@nightline_bp.route("/<string:name>/now", methods=["PATCH"])
def update_now(name):
    """Update the 'now' boolean of a nightline."""
    nightline = Nightline.get_nightline(name)

    data = request.get_json()
    if not data or "now" not in data:
        raise ValueError("Missing 'now' field")

    if not isinstance(data["now"], bool):
        raise ValueError("'now' must be a boolean")

    nightline.set_now(data["now"])

    return jsonify({
        "now": nightline.now
    }), 200
