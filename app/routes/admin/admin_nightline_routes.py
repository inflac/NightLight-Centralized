from typing import TYPE_CHECKING, Dict, Tuple, cast

from flask_restx import Namespace, Resource, abort

from app.models import Nightline
from app.routes.api_models import (
    admin_nightline_model,
    api_key_model,
    error_model,
    success_model,
)
from app.routes.decorators import require_admin_key, sanitize_nightline_name

if TYPE_CHECKING:
    from app.models.apikey import ApiKey

admin_nightline_ns = Namespace("admin nightline", description="Admin routes for nightlines - API key required", security="apikey")

ad_nl_error_model = admin_nightline_ns.model("Error", error_model)
ad_nl_success_model = admin_nightline_ns.model("Success", success_model)
ad_nl_api_key_model = admin_nightline_ns.model("API-Key", api_key_model)
ad_nl_admin_nightline_model = admin_nightline_ns.model("Admin Nightline", admin_nightline_model)


@admin_nightline_ns.route("/<string:nightline_name>")
class NightlineResource(Resource):  # type: ignore
    @sanitize_nightline_name
    @require_admin_key
    @admin_nightline_ns.response(200, "Success", ad_nl_admin_nightline_model)  # type: ignore[misc]
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)  # type: ignore[misc]
    @admin_nightline_ns.response(404, "Nightline Not Found", ad_nl_error_model)  # type: ignore[misc]
    def get(self, nightline_name: str) -> tuple[dict[str, object], int]:
        """Retrieve details of a specific nightline"""
        nightline = Nightline.get_nightline(nightline_name)
        if not nightline:
            abort(404, f"Nightline '{nightline_name}' not found")
        nightline = cast(Nightline, nightline)  # For mypi to know the correc type

        response = {
            "nightline_id": nightline.id,
            "nightline_name": nightline.name,
            "status_name": nightline.status.name,
            "instagram_media_id": nightline.instagram_media_id,
            "now": nightline.now,
        }
        return response, 200

    @sanitize_nightline_name
    @require_admin_key
    @admin_nightline_ns.response(200, "Success", ad_nl_success_model)  # type: ignore[misc]
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)  # type: ignore[misc]
    def post(self, nightline_name: str) -> Tuple[Dict[str, str], int]:
        """Add a new nightline with the default status"""
        nightline = Nightline.add_nightline(nightline_name)
        if not nightline:
            abort(
                400,
                message=f"Nightline '{nightline_name}' could not be added due to invalid data or duplication",
            )

        response = {"message": f"Nightline '{nightline_name}' added successfully"}
        return response, 200

    @sanitize_nightline_name
    @require_admin_key
    @admin_nightline_ns.response(200, "Success", ad_nl_success_model)  # type: ignore[misc]
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)  # type: ignore[misc]
    def delete(self, nightline_name: str) -> Tuple[Dict[str, str], int]:
        """Remove a nightline by name"""
        nightline = Nightline.remove_nightline(nightline_name)
        if not nightline:
            abort(400, f"Nightline '{nightline_name}' could not be removed")

        response = {"message": f"Nightline '{nightline_name}' removed successfully"}
        return response, 200


@admin_nightline_ns.route("/key/<string:nightline_name>")
class ApiKeyResource(Resource):  # type: ignore
    @sanitize_nightline_name  # Can return 400 error
    @require_admin_key
    @admin_nightline_ns.response(200, "Success", ad_nl_api_key_model)  # type: ignore[misc]
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)  # type: ignore[misc]
    @admin_nightline_ns.response(404, "Nightline Not Found", ad_nl_error_model)  # type: ignore[misc]
    @admin_nightline_ns.response(500, "API-Key Error", ad_nl_error_model)  # type: ignore[misc]
    def get(self, nightline_name: str) -> Tuple[Dict[str, str], int]:
        """Get the API-Key of a nightline"""
        nightline = Nightline.get_nightline(nightline_name)
        if not nightline:
            abort(404, f"Nightline '{nightline_name}' not found")
        nightline = cast(Nightline, nightline)

        api_key = nightline.get_api_key()
        if not api_key:
            abort(500, f"No api key found for nightline: '{nightline_name}'")
        api_key = cast("ApiKey", api_key)

        return {"API-Key": f"{api_key.key}"}, 200

    @sanitize_nightline_name  # Can return 400 error
    @require_admin_key
    @admin_nightline_ns.response(200, "Success", ad_nl_success_model)  # type: ignore[misc]
    @admin_nightline_ns.response(400, "Bad Request", ad_nl_error_model)  # type: ignore[misc]
    @admin_nightline_ns.response(404, "Nightline Not Found", ad_nl_error_model)  # type: ignore[misc]
    @admin_nightline_ns.response(500, "API-Key Error", ad_nl_error_model)  # type: ignore[misc]
    def patch(self, nightline_name: str) -> Tuple[Dict[str, str], int]:
        """Renew the API-Key of a nightline"""
        nightline = Nightline.get_nightline(nightline_name)
        if not nightline:
            abort(404, f"Nightline '{nightline_name}' not found")
        nightline = cast(Nightline, nightline)  # For mypi to know the correct type

        if not nightline.renew_api_key():
            abort(500, f"No api key found for nightline: '{nightline_name}'")

        return {"message": "API key regenerated successfully"}, 200
