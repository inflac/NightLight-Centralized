from flask import request
from flask_restx import Namespace, Resource, abort

from app.routes.api_models import nightline_status_model, nightline_now_model
from app.models import Nightline
from app.routes.decorators import sanitize_name

nightline_ns = Namespace(
    "nightline",
    description="Routes for nightlines - API key required")

# Define the request model for the update status and now boolean
nl_status_model = nightline_ns.model(
    'Nightline Status', nightline_status_model)
nl_now_model = nightline_ns.model('Nightline Now', nightline_now_model)

@nightline_ns.route("/<string:name>")
class NightlineStatusResource(Resource):
    @sanitize_name
    @nightline_ns.expect(nl_status_model)
    @nightline_ns.response(200, "Success", nl_status_model)
    @nightline_ns.response(400, "Bad Request")
    @nightline_ns.response(404, "Nightline Not Found")
    @nightline_ns.marshal_with(nl_status_model)
    def patch(self, name):
        """Set the status of a nightline."""
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        # Parse and validate request body
        data = request.get_json(force=True, silent=True)
        if not data or "status" not in data:
            abort(400, "Missing 'status' field in request.")

        status_value = data["status"]
        if not isinstance(status_value, str) or not status_value.strip():
            abort(400, "'status' must be a non-empty string.")

        nightline.set_status(status_value.strip())

        response = {**nightline.status.__dict__, "now": nightline.now}
        return response, 200

@nightline_ns.route("/<string:name>/now")
class NightlineNowResource(Resource):
    @sanitize_name
    @nightline_ns.expect(nl_now_model)
    @nightline_ns.response(200, "Success", nl_now_model)
    @nightline_ns.response(400, "Bad Request")
    @nightline_ns.response(404, "Nightline Not Found")
    @nightline_ns.marshal_with(nl_now_model)
    def patch(self, name):
        """Update the 'now' boolean of a nightline."""
        # Fetch the nightline entry
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, f"Nightline '{name}' not found")

        # Parse and validate request body
        # Ensures JSON parsing doesn't throw an error
        data = request.get_json(force=True, silent=True)
        if not data or "now" not in data:
            abort(400, "Missing 'now' field in request.")

        now_value = data.get("now")
        if not isinstance(now_value, bool):  # More robust boolean check
            abort(400, "'now' must be a boolean.")

        # Update and persist the change
        nightline.set_now(now_value)
        return {"now": nightline.now}, 200
