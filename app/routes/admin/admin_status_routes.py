from flask import Blueprint, jsonify, request
from ...models import Status

admin_status_bp = Blueprint('admin_status', __name__)

# Route to get a specific status by name
@admin_status_bp.route('/<name>', methods=['GET'])
def get_status(name):
    status = Status.get_status(name)

    return jsonify({
        "name": status.name,
        "description_de": status.description_de,
        "description_en": status.description_en
    }), 200

# Route to add a new status
@admin_status_bp.route('/<string:name>', methods=['POST'])
def add_status(name):
    data = request.get_json()

    # Validate input
    if not all(key in data for key in ("description_de", "description_en")):
        raise ValueError("Missing required fields")

    description_de = data["description_de"]
    description_en = data["description_en"]

    # Call the add_status method from the Status model
    status = Status.add_status(name, description_de, description_en)

    return jsonify({
        "message": "Status created successfully",
        "name": status.name,
        "description_de": status.description_de,
        "description_en": status.description_en
    }), 201

# Route to remove a status
@admin_status_bp.route('/<string:name>', methods=['DELETE'])
def remove_status(name):
    Status.remove_status(name)

    return jsonify({"message": f"Status '{name}' removed successfully."}), 200

# Route to list all statuses
@admin_status_bp.route('/statuses', methods=['GET'])
def list_status():
    statuses = Status.list_status()

    return jsonify(statuses), 200
