from flask import jsonify
from flask_restx import Namespace, Resource
from app.models import Nightline

admin_nightline_ns = Namespace(
    "admin nightline",
    description="Admin routes for nightlines")

@admin_nightline_ns.route("/<string:name>")
class NightlineResource(Resource):
    def get(self, name):
        """Retrieve details of a specific nightline."""
        nightline = Nightline.get_nightline(name)
        return jsonify({
            "name": nightline.name,
            "status": nightline.status.name,
            "instagram_media_id": nightline.instagram_media_id
        })

    def post(self, name):
        """Add a new nightline with the default status."""
        new_nightline = Nightline.add_nightline(name)
        return jsonify({
            "message": "Nightline added successfully",
            "id": new_nightline.id,
            "name": new_nightline.name,
            "status": new_nightline.status.name
        }), 201

    def delete(self, name):
        """Remove a nightline by name."""
        Nightline.remove_nightline(name)
        return jsonify(
            {"message": f"Nightline '{name}' removed successfully."})

@admin_nightline_ns.route("/all")
class NightlineListResource(Resource):
    def get(self):
        """List all nightlines."""
        cities = Nightline.list_cities()
        return jsonify(cities)
