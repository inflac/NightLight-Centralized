from flask import Blueprint, jsonify
from ..models import Nightline

public_bp = Blueprint("public", __name__)

# Route to get the status of a nightline
@public_bp.route("/<string:name>/status", methods=["GET"])
def get_status(name):
    """Retrieve the status of a nightline"""
    nightline = Nightline.get_nightline(name)

    return jsonify({
        "status": nightline.status
    }), 200
