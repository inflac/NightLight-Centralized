from typing import Any, Dict, List, Tuple, Union

from flask import Response, request
from flask_restx import Namespace, Resource, abort

from app.models import Status
from app.routes.api_models import (
    error_model,
    set_status_model,
    status_model,
    success_model,
)
from app.routes.decorators import require_admin_key
from app.validation import validate_request_body, validate_status_value

admin_status_ns = Namespace("admin status", description="Admin routes for statuses - API key required", security="apikey")

# Define the request and response model for the status
ad_st_error_model = admin_status_ns.model("Error", error_model)
ad_st_success_model = admin_status_ns.model("Success", success_model)
ad_st_status_model = admin_status_ns.model("Status", status_model)
ad_st_set_status_model = admin_status_ns.model("Set Status", set_status_model)


@admin_status_ns.route("/")
@admin_status_ns.doc(security="apikey")
class StatusResource(Resource):  # type: ignore
    @require_admin_key
    @admin_status_ns.expect(ad_st_status_model)  # type: ignore[misc]
    @admin_status_ns.response(200, "Success", ad_st_success_model)  # type: ignore[misc]
    @admin_status_ns.response(400, "Bad Request", ad_st_error_model)  # type: ignore[misc]
    def post(self) -> Tuple[Dict[str, str], int]:
        """Add a new status"""
        # Dynamically get required fields from the model
        required_fields = [field_name for field_name, _ in ad_st_status_model.items()]

        data = request.get_json()
        validate_request_body(data, required_fields)

        status_name = data["status_name"]
        data.pop("status_name")

        status = Status.add_status(name=status_name, **data)
        if not status:
            abort(
                400,
                message=f"Status '{status_name}' could not be added due to invalid data or duplication",
            )

        response = {"message": f"Status '{status_name}' added successfully"}
        return response, 200

    # Route to remove a status
    @require_admin_key
    @admin_status_ns.expect(ad_st_set_status_model)  # type: ignore[misc]
    @admin_status_ns.response(200, "Success", ad_st_success_model)  # type: ignore[misc]
    @admin_status_ns.response(400, "Bad Request", ad_st_error_model)  # type: ignore[misc]
    def delete(self) -> Tuple[Dict[str, str], int]:
        """Remove a status"""
        data = request.get_json()
        validate_request_body(data, ["status"])

        status_value = data["status"]
        validate_status_value(status_value)

        status = Status.remove_status(status_value)
        if not status:
            abort(400, f"Status '{status_value}' could not be removed")

        response = {"message": f"Status '{status_value}' removed successfully"}
        return response, 200


# Route to list all statuses
@admin_status_ns.route("/all")
@admin_status_ns.doc(security="apikey")
class StatusListResource(Resource):  # type: ignore
    @require_admin_key
    @admin_status_ns.response(200, "Success", [ad_st_status_model])  # type: ignore[misc]
    @admin_status_ns.response(404, "Statuses Not Found", ad_st_error_model)  # type: ignore[misc]
    def get(self) -> Union[Tuple[List[Dict[str, Any]], int], Response]:
        """List all selectable statuses"""
        statuses = Status.list_statuses()

        response = [
            {
                "status_name": status.name,
                "description_de": status.description_de,
                "description_en": status.description_en,
                "description_now_de": status.description_now_de,
                "description_now_en": status.description_now_en,
            }
            for status in statuses
        ]

        if not response:
            abort(404, "No statuses found")

        return response, 200
