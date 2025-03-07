from flask_restx import Namespace, Resource
from app.models import Nightline

admin_nightline_ns = Namespace(
    "admin nightline",
    description="Admin routes for nightlines - API key required")

@admin_nightline_ns.route("/<string:name>")
class NightlineResource(Resource):
    def get(self, name):
        """Retrieve details of a specific nightline."""
        nightline = Nightline.get_nightline(name)
        return {
            "name": nightline.name,
            "status": nightline.status.name,
            "instagram_media_id": nightline.instagram_media_id
        }, 200

    def post(self, name):
        """Add a new nightline with the default status."""
        new_nightline = Nightline.add_nightline(name)
        return {
            "message": "Nightline added successfully",
            "id": new_nightline.id,
            "name": new_nightline.name,
            "status": new_nightline.status.name
        }, 201

    def delete(self, name):
        """Remove a nightline by name."""
        Nightline.remove_nightline(name)
        return {"message": f"Nightline '{name}' removed successfully."}

@admin_nightline_ns.route("/<string:name>/renew_key")
class ApiKeyResource(Resource):
    def patch(self, name):
        """Renew the API-Key of a nightline"""
        nightline = Nightline.get_nightline(name)
        if not nightline:
            return {"message": f"Nightline '{name}' not found"}, 404

        nightline.renew_api_key()

        return {"message": "API key regenerated successfully"}, 200