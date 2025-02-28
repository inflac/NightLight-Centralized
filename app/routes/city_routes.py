from flask import Blueprint, jsonify, request
from models import City

city_bp = Blueprint("city", __name__)

# Route to get a specific city by name
@city_bp.route("/<string:name>", methods=["GET"])
def get_city(name):
    """Retrieve details of a specific city."""
    city = City.get_city(name)
    
    return jsonify({
        "id": city.id,
        "name": city.name,
        "status": city.status.status,  # Only return status name
        "instagram_media_id": city.instagram_media_id
    }), 200

# Route to add a new city
@city_bp.route("/<string:name>", methods=["POST"])
def add_city(name):
    """Add a new city with the default status."""
    new_city = City.add_city(name)
    
    return jsonify({
        "message": "City added successfully",
        "id": new_city.id,
        "name": new_city.name,
        "status": new_city.status.status
    }), 201

# Route to remove a city
@city_bp.route("/<string:name>", methods=["DELETE"])
def remove_city(name):
    """Remove a city by name."""
    City.remove_city(name)
    return jsonify({"message": f"City '{name}' removed successfully."}), 200

# Route to list all cities
@city_bp.route("/cities", methods=["GET"])
def list_cities():
    """List all cities."""
    cities = City.list_cities()
    return jsonify(cities), 200
