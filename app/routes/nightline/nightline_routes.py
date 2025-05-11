from flask import request
from flask_restx import Namespace, Resource, abort, reqparse
from werkzeug.datastructures import FileStorage

from app.validation import validate_request_body, validate_status_value, validate_instagram_credentials, validate_image
from app.routes.api_models import error_model, success_model, set_status_model, set_status_config_model, set_now_model, instagram_create_model
from app.models import Nightline, Status, NightlineStatus
from app.models import StorySlide
from app.routes.decorators import sanitize_name

nightline_ns = Namespace(
    "nightline",
    description="Routes for nightlines - API key required")

# Define the request model for the update status and now boolean
nl_error_model = nightline_ns.model("Error", error_model)
nl_success_model = nightline_ns.model("Success", success_model)
nl_set_status_model = nightline_ns.model("Set Status", set_status_model)
nl_set_status_config_model = nightline_ns.model(
    "Set Status Config", set_status_config_model)
nl_set_now_model = nightline_ns.model("Set Now", set_now_model)
nl_instagram_create_model = nightline_ns.model(
    "Instagram Credentials", instagram_create_model)

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('image', location='files', type=FileStorage, required=True, help='Image file')
upload_parser.add_argument(
    'status',
    location='form',
    type=str,
    required=True,
    help='Status name'
)

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
        validate_request_body(data, ["status"])

        status_value = data["status"]
        validate_status_value(status_value)  # Validate status name format

        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        status = nightline.set_status(status_value.strip())
        if not status:
            abort(500, f"Updating the status failed")

        response = {
            "message": f"Status successfully updated to: {status_value}"}
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

@nightline_ns.route("/<string:name>/status/config")
class NightlineStatusConfigResource(Resource):
    @sanitize_name
    @nightline_ns.expect(nl_set_status_config_model)
    @nightline_ns.response(200, "Success", nl_success_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    @nightline_ns.response(500, "Status Error", nl_error_model)
    def patch(self, name):
        """Configure a status of a nightline"""
        # Parse and validate request body
        data = request.get_json(force=True, silent=True)
        validate_request_body(data, ["status", instagram_story])

        instagram_story = data.get("instagram_story")
        if not isinstance(instagram_story, bool):
            abort(400, "'instagram_story' must be a boolean")

        status_value = data["status"]
        validate_status_value(status_value)  # Validate status name format

        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        status = Status.get_status(status_value)

        if not NightlineStatus.update_instagram_story(
                nightline, status, instagram_story):
            abort(500, f"Updating the status failed")

        response = {"message": f"Status successfully updated"}
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
        # Parse and validate request body
        data = request.get_json(force=True, silent=True)
        validate_request_body(data, ["now"])

        now_value = data.get("now")
        if not isinstance(now_value, bool):
            abort(400, "'now' must be a boolean")

        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        # Update and persist the change
        nightline.set_now(now_value)

        response = {"message": f"Now value successfully set to '{now_value}'"}
        return response, 200

@nightline_ns.route("/<string:name>/instagram")
class NightlineInstagramResource(Resource):
    @sanitize_name
    # Expect the data for creating Instagram account
    @nightline_ns.expect(nl_instagram_create_model)
    @nightline_ns.response(201, "Created", nl_success_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    def post(self, name):
        """Add an Instagram account for the given nightline"""
        # Parse and validate the request body
        data = request.get_json(force=True, silent=True)
        validate_request_body(data, ["username", "password"])

        username = data["username"]
        password = data["password"]
        validate_instagram_credentials(username, password)

        # Fetch the nightline entry
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

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
        # Parse and validate the request body
        data = request.get_json(force=True, silent=True)
        validate_request_body(data, ["username", "password"])

        # Validate the submitted instagram credentials format
        username = data["username"]
        password = data["password"]
        validate_instagram_credentials(username, password)
        
        # Fetch the nightline entry
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        # Fetch the Instagram account
        instagram_account = nightline.instagram_account
        if not instagram_account:
            abort(404, "Instagram account not found for this nightline")

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
    

@nightline_ns.route("/<string:name>/story")
class NightlineStoryResource(Resource):
    @sanitize_name
    # Expect the story slide data
    @nightline_ns.expect(upload_parser, validate=True)
    @nightline_ns.response(201, "Created", nl_success_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    @nightline_ns.response(500, "Story Error", nl_error_model)
    def post(self, name):
        """Add a story slide for the given nightline and status"""
        # Parse the request body
        args = upload_parser.parse_args()
        validate_request_body(args, ["status", "image"])

        status_value = args['status']
        validate_status_value(status_value)  # Validate status name format

        image_file = args['image']
        validate_image(image_file)  # Validate image file

        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        nightline_status = next(
            (nightline_status for nightline_status in nightline.nightline_statuses if nightline_status.status.name == status_value),
            None
        )

        if not StorySlide.update_story_slide(image_file, nightline_status):
            abort(500, f"Uploading a story slide for status {status_value} failed")

        response = {"message": f"Story for status {status_value} added successfully"}
        return response, 201

    @sanitize_name
    @nightline_ns.response(200, "Success", nl_success_model)
    @nightline_ns.response(400, "Bad Request", nl_error_model)
    @nightline_ns.response(404, "Nightline Not Found", nl_error_model)
    @nightline_ns.response(500, "Story Error", nl_error_model)
    def delete(self, name):
        """Remove a story slide for the given nightline and status"""
        # Parse the request body
        args = upload_parser.parse_args()
        validate_request_body(args, ["status"])

        status_value = args['status']
        validate_status_value(status_value)  # Validate status name format

        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        nightline_status = next(
            (nightline_status for nightline_status in nightline.nightline_statuses if nightline_status.status.name == status_value),
            None
        )

        if not StorySlide.remove_story_slide(nightline_status):
            abort(500, f"Deleting a story slide for status {status_value} failed")

        response = {"message": f"Story for status {status_value} removed successfully"}
        return response, 200
