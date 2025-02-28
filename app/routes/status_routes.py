from flask import Blueprint, request, jsonify
from models import Status

status_bp = Blueprint('status', __name__)

# Route to get a specific status by name
@status_bp.route('/<status_name>', methods=['GET'])
def get_status(status_name):
    status = Status.get_status(status_name)
    
    return jsonify({
        "id": status.id,
        "status": status.status,
        "description_de": status.description_de,
        "description_en": status.description_en
    }), 200

# Route to add a new status
@status_bp.route('/<string:status>', methods=['POST'])
def add_status(status):
    data = request.get_json()

    # Validate input
    if not all(key in data for key in ("description_de", "description_en")):
        raise ValueError("Missing required fields")

    description_de = data["description_de"]
    description_en = data["description_en"]

    # Call the add_status method from the Status model
    created_status = Status.add_status(status, description_de, description_en)

    return jsonify({
        "message": "Status created successfully",
        "status": created_status.status,
        "description_de": created_status.description_de,
        "description_en": created_status.description_en
    }), 201

# Route to remove a status
@status_bp.route('/<string:status>', methods=['DELETE'])
def remove_status(status):
    Status.remove_status(status)

    return jsonify({"message": f"Status '{status}' removed successfully."}), 200

# Route to list all statuses
@status_bp.route('/statuses', methods=['GET'])
def list_status():
    statuses = Status.list_status()

    return jsonify(statuses), 200
