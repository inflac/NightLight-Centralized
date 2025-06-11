from flask_restx import Namespace, Resource, abort

from app.models import Nightline
from app.routes.api_models import (
    admin_nightline_model,
    api_key_model,
    error_model,
    success_model,
)
from app.routes.decorators import sanitize_name

admin_nightline_ns = Namespace(
    "admin nightline", description="Admin routes for nightlines - API key required"
)

ad_nl_error_model = admin_nightline_ns.model("Error", error_model)
ad_nl_success_model = admin_nightline_ns.model("Success", success_model)
ad_nl_api_key_model = admin_nightline_ns.model("API-Key", api_key_model)
ad_nl_admin_nightline_model = admin_nightline_ns.model(
    "Admin Nightline", admin_nightline_model
)


@admin_nightline_ns.route("/<string:name>")
class NightlineResource(Resource):
    @sanitize_name
    @admin_nightline_ns.response(200, "Success", ad_nl_admin_nightline_model)
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)
    @admin_nightline_ns.response(404, "Nightline Not Found", ad_nl_error_model)
    def get(self, name):
        """Retrieve details of a specific nightline"""
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        response = {
            "nightline_id": nightline.id,
            "nightline_name": nightline.name,
            "status_name": nightline.status.name,
            "instagram_media_id": nightline.instagram_media_id,
            "now": nightline.now,
        }
        return response, 200

    @sanitize_name
    @admin_nightline_ns.response(200, "Success", ad_nl_success_model)
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)
    def post(self, name):
        """Add a new nightline with the default status"""
        nightline = Nightline.add_nightline(name)
        if not nightline:
            abort(
                400,
                message=f"Nightline '{name}' could not be added due to invalid data or duplication",
            )

        response = {"message": f"Nightline '{name}' added successfully"}
        return response, 200

    @sanitize_name
    @admin_nightline_ns.response(200, "Success", ad_nl_success_model)
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)
    def delete(self, name):
        """Remove a nightline by name"""
        nightline = Nightline.remove_nightline(name)
        if not nightline:
            abort(400, f"Nightline '{name}' could not be removed")

        response = {"message": f"Nightline '{name}' removed successfully"}
        return response, 200


@admin_nightline_ns.route("/key/<string:name>")
class ApiKeyResource(Resource):
    @sanitize_name  # Can return 400 error
    @admin_nightline_ns.response(200, "Success", ad_nl_api_key_model)
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)
    @admin_nightline_ns.response(404, "Nightline Not Found", ad_nl_error_model)
    @admin_nightline_ns.response(500, "API-Key Error", ad_nl_error_model)
    def get(self, name):
        """Get the API-Key of a nightline"""
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        api_key = nightline.get_api_key()
        if not api_key:
            abort(500, "No api key found for nightline: '{name}'")

        return {"API-Key": f"{api_key.key}"}, 200

    @sanitize_name  # Can return 400 error
    @admin_nightline_ns.response(200, "Success", ad_nl_success_model)
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)
    @admin_nightline_ns.response(404, "Nightline Not Found", ad_nl_error_model)
    @admin_nightline_ns.response(500, "API-Key Error", ad_nl_error_model)
    def patch(self, name):
        """Renew the API-Key of a nightline"""
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        if not nightline.renew_api_key():
            abort(500, "No api key found for nightline: '{name}'")

        return {"message": "API key regenerated successfully"}, 200
