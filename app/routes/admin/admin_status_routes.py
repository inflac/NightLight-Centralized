from flask import request
from flask_restx import Namespace, Resource, abort

from app.routes.api_models import status_model
from app.models import Status

admin_status_ns = Namespace(
    "admin status",
    description="Admin routes for statuses")

# Define the request and response model for the status
ad_status_model = admin_status_ns.model("Status", status_model)

@admin_status_ns.route("/<string:name>")
class StatusResource(Resource):
    @admin_status_ns.expect(ad_status_model)
    @admin_status_ns.marshal_with(ad_status_model)  # Define the response format for success
    def post(self, name):
        data = request.get_json()

        # Validate input (RESTX validation will be handled with model)
        description_de = data["description_de"]
        description_en = data["description_en"]
        description_now_de = data["description_now_de"]
        description_now_en = data["description_now_en"]

        # Call the add_status method from the Status model
        status = Status.add_status(name, description_de, description_en, description_now_de, description_now_en)

        return {
            "message": "Status created successfully",
            "name": status.name,
            "description_de": status.description_de,
            "description_en": status.description_en,
            "description_now_de": status.description_now_de,
            "description_now_en": status.description_now_en,
        }, 201

    # Route to remove a status
    def delete(self, name):
        Status.remove_status(name)
        return {"message": f"Status '{name}' removed successfully."}, 200

# Route to list all statuses
@admin_status_ns.route("/all")
class StatusListResource(Resource):
    def get(self):
        statuses = Status.list_status()
        return statuses, 200
