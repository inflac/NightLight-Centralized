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

@admin_status_ns.route("/<string:name>")
class StatusResource(Resource):
    @sanitize_name
    @admin_status_ns.expect(ad_st_status_model)
    @admin_status_ns.response(200, "Success", ad_nl_success_model)
    @admin_status_ns.response(400, "Bad Request", ad_st_error_model)

    def post(self, name):
        data = request.get_json()

        # TODO Handle the necessary data and validate/sanitize it
        description_de = data["description_de"]
        description_en = data["description_en"]
        description_now_de = data["description_now_de"]
        description_now_en = data["description_now_en"]

        status = Status.add_status(
            name,
            description_de,
            description_en,
            description_now_de,
            description_now_en)
        if not status:
            abort(400, message=f"Status '{name}' could not be added due to invalid data or duplication")

        response = {"message": f"Status '{name}' added successfully"}
        return response, 200

    # Route to remove a status
    @sanitize_name
    @admin_status_ns.response(200, "Success", ad_nl_success_model)
    @admin_status_ns.response(400, "Bad Request", ad_st_error_model)
    def delete(self, name):
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
