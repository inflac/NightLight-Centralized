from flask import request
from flask_restx import Namespace, Resource, abort

from app.routes.api_models import error_model, success_model, status_model
from app.models import Status
from app.routes.decorators import sanitize_name


admin_status_ns = Namespace(
    "admin status",
    description="Admin routes for statuses - API key required")

# Define the request and response model for the status
ad_st_error_model = admin_status_ns.model("Error", error_model)
ad_nl_success_model = admin_status_ns.model("Success", success_model)
ad_st_status_model = admin_status_ns.model("Status", status_model)

@admin_status_ns.route("/")
class StatusResource(Resource):
    @admin_status_ns.expect(ad_st_status_model)
    @admin_status_ns.response(200, "Success", ad_nl_success_model)
    @admin_status_ns.response(400, "Bad Request", ad_st_error_model)
    def post(self):
        data = request.get_json()
        if not data:
            abort(
                400,
                message="Invalid JSON payload. Request body is missing or malformed")

        # Dynamically get required fields from the model
        required_fields = [
            field_name for field_name, _ in ad_st_status_model.items()
        ]

        # Validate and sanitize input
        sanitized_data = {}
        for field in required_fields:
            value = data.get(field, "").strip()
            if not value:
                abort(
                    400, message=f"Missing or empty required field: '{field}'")
            if len(value) > 200:
                abort(
                    400, message=f"'{field}' is too long (max 200 characters)")
            sanitized_data[field] = value

        status_name = sanitized_data.get("status_name")
        sanitized_data.pop("status_name")

        status = Status.add_status(name=status_name, **sanitized_data)
        if not status:
            abort(
                400,
                message=f"Status '{status_name}' could not be added due to invalid data or duplication")

        response = {"message": f"Status '{status_name}' added successfully"}
        return response, 200

    # Route to remove a status
    @admin_status_ns.response(200, "Success", ad_nl_success_model)
    @admin_status_ns.response(400, "Bad Request", ad_st_error_model)
    def delete(self):
        data = request.get_json()
        if not data or "name" not in data:
            abort(400, message="Missing 'name' field in the request body")

        name = data["name"]
        if len(name) > 15 or not name.isalnum():
            abort(400, message="The value for 'name' is not a valid status name")

        status = Status.remove_status(name)
        if not status:
            abort(400, f"Status '{name}' could not be removed")

        response = {"message": f"Status '{name}' removed successfully"}
        return response, 200

# Route to list all statuses
@admin_status_ns.route("/all")
class StatusListResource(Resource):
    @admin_status_ns.response(200, "Success", [ad_st_status_model])
    @admin_status_ns.response(404, "Statuses Not Found", ad_st_error_model)
    def get(self):
        statuses = Status.list_status()

        response = [{
            'status_name': status.name,
            'description_de': status.description_de,
            'description_en': status.description_en,
            'description_now_de': status.description_now_de,
            'description_now_en': status.description_now_en,
        } for status in statuses]

        if not response:
            abort(404, "No statuses found")

        return response, 200
