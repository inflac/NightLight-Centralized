from flask import request
from flask_restx import Namespace, Resource, abort
from sqlalchemy import or_

from app.routes.api_models import error_model, nightline_status_model
from app.models import Nightline, Status
from app.routes.decorators import sanitize_name


public_ns = Namespace(
    "public",
    description="Public accessible routes")

# Define the response model for nightline status
pb_error_model = public_ns.model("Error", error_model)
pb_nightline_status_model = public_ns.model(
    "Nightline Status", nightline_status_model)

@public_ns.route("/<string:name>")
class PublicNightlineStatusResource(Resource):
    @sanitize_name
    @public_ns.response(200, "Success", pb_nightline_status_model)
    # Can be returend by sanitize_name
    @public_ns.response(400, "Bad Request", pb_error_model)
    @public_ns.response(404, "Nightline Not Found", pb_error_model)
    def get(self, name):
        """Retrieve the status of a nightline"""
        nightline = Nightline.get_nightline(name)
        if not nightline:
            abort(404, message=f"Nightline '{name}' not found")

        response = {
            'nightline_name': nightline.name,
            'status_name': nightline.status.name,
            'description_de': nightline.status.description_de,
            'description_en': nightline.status.description_en,
            'description_now_de': nightline.status.description_now_de,
            'description_now_en': nightline.status.description_now_en,
            'now': nightline.now,
        }
        return response, 200

# Resource to get the statuses of all nightlines with filter options
@public_ns.route("/all")
class PublicNightlineListResource(Resource):
    @public_ns.param("status",
                     "Filter for the current status (e.g., 'default' or 'german-english'). Optional.")
    @public_ns.param("language",
                     "Language filter for to only include nightlines speaking a certain language. Optional.")
    @public_ns.param("now", "Filter for nightlines that are currently available ('true' or 'false'). Optional.")
    @public_ns.response(200, "Success", [pb_nightline_status_model])
    @public_ns.response(400, "Bad Request", pb_error_model)
    def get(self):
        """Retrieve the statuses of all nightlines with filter options"""
        status_filter = request.args.get("status")
        language_filter = request.args.get("language")
        now_filter = request.args.get("now")

        query = Nightline.query
        query = query.join(Status, Nightline.status)

        # Apply filters
        if status_filter:
            query = query.filter(Nightline.status.has(name=status_filter))

        if language_filter:
            # Use 'or_' to combine conditions for multiple possible values of
            # status.name
            if language_filter == "de":
                query = query.filter(
                    or_(
                        Status.name == "german",
                        Status.name == "german-english"
                    )
                )
            elif language_filter == "en":
                query = query.filter(
                    or_(
                        Status.name == "english",
                        Status.name == "german-english"
                    )
                )
            else:
                abort(
                    400,
                    f"Invalid language filter value: {language_filter}. Only 'en' and 'de' are allowed.")

        if now_filter:
            query = query.filter(
                Nightline.now == (now_filter.lower() == "true"))

        # Fetch nightlines that match filter criteria
        nightlines = query.all()

        response = [{
            'nightline_name': nightline.name,
            'status_name': nightline.status.name,
            'description_de': nightline.status.description_de,
            'description_en': nightline.status.description_en,
            'description_now_de': nightline.status.description_now_de,
            'description_now_en': nightline.status.description_now_en,
            'now': nightline.now,
        } for nightline in nightlines]
        return response, 200
