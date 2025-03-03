from flask import request
from flask_restx import Namespace, Resource

from app.routes.api_models import nightline_filter_model, nightline_status_model
from app.models import Nightline

public_ns = Namespace(
    "public",
    description="Public accessible routes")

# Define the request model for filtering
public_filter_model = public_ns.model("Nightline Status Filter", nightline_filter_model)
# Define the response model for nightline status
nightline_status_model = public_ns.model("Nightline Status", nightline_status_model)

@public_ns.route("/<string:name>")
class NightlineStatusResource(Resource):
    def get(self, name):
        """Retrieve the status of a nightline"""
        nightline = Nightline.get_nightline(name)
        return {
            "status": nightline.status.name,
            "description_de": nightline.status.description_de,
            "description_en": nightline.status.description_en,
            "description_now_de": nightline.status.description_now_de,
            "description_now_en": nightline.status.description_now_en,
            "now": nightline.now
        }, 200

# Resource to get the statuses of all nightlines with filter options
@public_ns.route("/all")
class NightlineListResource(Resource):
    @public_ns.expect(public_filter_model, validate=True)
    @public_ns.marshal_with(nightline_status_model, as_list=True)
    def get(self):
        """Retrieve the statuses of all nightlines with filter options"""
        status_filter = request.args.get("status")
        language_filter = request.args.get("language")
        now_filter = request.args.get("now")

        # Build the query
        query = Nightline.query

        # Apply filters
        if status_filter:
            query = query.filter(Nightline.status.has(name=status_filter))

        if language_filter:
            if language_filter == 'de':
                query = query.filter(
                    Nightline.status.name.in_(["german", "german-english"]))
            elif language_filter == 'en':
                query = query.filter(
                    Nightline.status.name.in_(["english", "german-english"]))

        if now_filter:
            query = query.filter(Nightline.now == (now_filter.lower() == 'true'))

        # Fetch the filtered nightlines
        nightlines = query.all()

        return nightlines, 200