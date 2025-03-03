from flask import request
from flask_restx import Namespace, Resource, fields

from app.routes.api_models import nightline_status_model, nightline_now_model
from app.models import Nightline

nightline_ns = Namespace(
    "nightline",
    description="Routes for nightlines - API Key required")

# Define the request model for the update status and now boolean
nightline_status_model = nightline_ns.model('Nightline Status', nightline_status_model)

nightline_now_model = nightline_ns.model('Nightline Now', nightline_now_model)

@nightline_ns.route("/<string:name>")
class NightlineStatusResource(Resource):
    @nightline_ns.expect(nightline_status_model)
    def patch(self, name):
        """Set the status of a nightline."""
        nightline = Nightline.get_nightline(name)

        data = request.get_json()
        if not data or "status" not in data:
            return {"message": "Status not found in data"}, 400

        nightline.set_status(data["status"])

        return {"status": nightline.status}, 200

# Resource to update the 'now' boolean of a nightline
@nightline_ns.route("/<string:name>/now")
class NightlineNowResource(Resource):
    @nightline_ns.expect(nightline_now_model)
    def patch(self, name):
        """Update the 'now' boolean of a nightline."""
        nightline = Nightline.get_nightline(name)

        data = request.get_json()
        if not data or "now" not in data:
            return {"message": "Missing 'now' field"}, 400

        if not isinstance(data["now"], bool):
            return {"message": "'now' must be a boolean"}, 400

        nightline.set_now(data["now"])

        return {"now": nightline.now}, 200