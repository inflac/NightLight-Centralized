from flask import Blueprint, jsonify, request
from ...models import Nightline

admin_nightline_bp = Blueprint("admin_nightline", __name__)

# Route to add a new nightline
@admin_nightline_bp.route("/<string:name>", methods=["POST"])
def add_nightline(name):
    """Add a new nightline with the default status."""
    new_nightline = Nightline.add_nightline(name)

    return jsonify({
        "message": "Nightline added successfully",
        "id": new_nightline.id,
        "name": new_nightline.name,
        "status": new_nightline.status.name
    }), 201

# Route to remove a nightline
@admin_nightline_bp.route("/<string:name>", methods=["DELETE"])
def remove_nightline(name):
    """Remove a nightline by name."""
    Nightline.remove_nightline(name)
    return jsonify({"message": f"Nightline '{name}' removed successfully."}), 200

# Route to list all cities
@admin_nightline_bp.route("/cities", methods=["GET"])
def list_cities():
    """List all cities."""
    cities = Nightline.list_cities()
    return jsonify(cities), 200
