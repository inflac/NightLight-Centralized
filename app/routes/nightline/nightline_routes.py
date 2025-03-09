from flask import request
from flask_restx import Namespace, Resource, abort

from app.routes.api_models import error_model, success_model, set_status_model, set_now_model, instagram_create_model
from app.models import Nightline
from app.routes.decorators import sanitize_name

nightline_ns = Namespace(
    "nightline",
    description="Routes for nightlines - API key required")

# Define the request model for the update status and now boolean
nl_error_model = nightline_ns.model("Error", error_model)
nl_success_model = nightline_ns.model("Success", success_model)
nl_set_status_model = nightline_ns.model("Set Status", set_status_model)
nl_set_now_model = nightline_ns.model("Set Now", set_now_model)
nl_instagram_create_model = nightline_ns.model("Instagram Credentials", instagram_create_model)

@nightline_ns.route("/<string:name>/status")
class NightlineStatusResource(Resource):
    @sanitize_name
    @nightline_ns.expect(nl_set_status_model)
    @nightline_ns.response(200, "Success", nl_success_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    @nightline_ns.response(500, "Status Error", nl_error_model)

    def patch(self, name):
        """Set the status of a nightline"""
        # Parse and validate request body
        data = request.get_json(force=True, silent=True)
        if not data or "status" not in data:
            abort(400, "Missing 'status' field in request")

        status_value = data["status"]
        if not isinstance(status_value, str) or not status_value.strip() or len(status_value) > 15:
            abort(400, "'status' must be a non-empty valid status name")

        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        status = nightline.set_status(status_value.strip())
        if not status:
            abort(500, f"Updating the status failed")

        response = {"message": f"Status successfully updated to: {status_value}"}
        return response, 200

    @sanitize_name
    @nightline_ns.response(200, "Success", nl_set_status_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    @nightline_ns.response(500, "Status Error", nl_error_model)
    def delete(self, name):
        """Reset the status of a nightline"""
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        status = nightline.reset_status()
        if not status:
            abort(500, f"Resetting the status failed")

        response = {"message": "Status successfully reset to: 'default'"}
        return response, 200

@nightline_ns.route("/<string:name>/now")
class NightlineNowResource(Resource):
    @sanitize_name
    @nightline_ns.expect(nl_set_now_model)
    @nightline_ns.response(200, "Success", nl_success_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    def patch(self, name):
        """Update the 'now' boolean of a nightline"""
        # Fetch the nightline entry
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        # Parse and validate request body
        # Ensures JSON parsing doesn't throw an error
        data = request.get_json(force=True, silent=True)
        if not data or "now" not in data:
            abort(400, "Missing 'now' field in request")

        now_value = data.get("now")
        if not isinstance(now_value, bool):  # More robust boolean check
            abort(400, "'now' must be a boolean")

        # Update and persist the change
        nightline.set_now(now_value)

        response = {"message": f"Now value successfully set to '{now_value}'"}
        return response, 200

@nightline_ns.route("/<string:name>/instagram")
class NightlineInstagramResource(Resource):
    @sanitize_name
    @nightline_ns.expect(nl_instagram_create_model)  # Expect the data for creating Instagram account
    @nightline_ns.response(201, "Created", nl_success_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    def post(self, name):
        """Add an Instagram account for the given nightline"""
        # Fetch the nightline entry
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        # Parse and validate the request data
        data = request.get_json(force=True, silent=True)
        if not data or "username" not in data or "password" not in data:
            abort(400, "Missing 'username' or 'password' in request")

        username = data["username"]
        password = data["password"]

        if len(username) > 50 or len(password) > 100:
            abort(400, "Invalid 'username' or 'password' in request")

        # Add the Instagram account
        if not nightline.add_instagram_account(username, password):
            abort(400, "There already exists an Instagram account for this nightline")

        response = {"message": "Instagram account added successfully"}
        return response, 201

    @sanitize_name
    @nightline_ns.expect(nl_instagram_create_model)
    @nightline_ns.response(200, "Success", nl_success_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    def patch(self, name):
        """Update the Instagram credentials for the given nightline"""
        # Fetch the nightline entry
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        # Fetch the Instagram account
        instagram_account = nightline.instagram_account
        if not instagram_account:
            abort(404, "Instagram account not found for this nightline")

        # Parse and validate the request data
        data = request.get_json(force=True, silent=True)
        if not data or "username" not in data or "password" not in data:
            abort(400, "Missing 'username' or 'password' in request")

        username = data["username"]
        password = data["password"]

        if len(username) > 50 or len(password) > 100:
            abort(400, "Invalid 'username' or 'password' in request")

        instagram_account.set_username(username)
        instagram_account.set_password(password)

        response = {"message": "Instagram account data updated successfully"}
        return response, 200

    @sanitize_name
    @nightline_ns.response(200, "Success", nl_success_model)
    @nightline_ns.response(404, "Instagram Account Not Found", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    def delete(self, name):
        """Delete the Instagram account for the given nightline"""
        # Fetch the nightline entry
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        # Fetch the Instagram account
        instagram_account = nightline.instagram_account
        if not instagram_account:
            abort(404, "Instagram account not found for this nightline")

        # Delete the Instagram account
        nightline.delete_instagram_account()

        response = {"message": "Instagram account deleted successfully"}
        return response, 200
