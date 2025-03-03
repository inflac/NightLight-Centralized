from flask import request
from flask_restx import Namespace, Resource, fields

from app.routes.api_models import nightline_filter_model, nightline_status_model
from app.models import Nightline

public_ns = Namespace(
    "public",
    description="Public accessible routes")

# Define the response model for nightline status
pb_nl_status_model = public_ns.model(
    "Nightline Status", nightline_status_model)
# Define the request model for filtering
pb_nl_filter_model = public_ns.model(
    "Nightline Status Filter",
    nightline_filter_model)


@public_ns.route("/<string:name>")
class PublicNightlineStatusResource(Resource):
    @public_ns.marshal_with(pb_nl_status_model)
    def get(self, name):
        """Retrieve the status of a nightline"""
        nightline = Nightline.get_nightline(name)

        # Extend the response with `now` field
        response = {**nightline.status.__dict__, "now": nightline.now}
        return response, 200

# Resource to get the statuses of all nightlines with filter options
@public_ns.route("/all")
class PublicNightlineListResource(Resource):
    @public_ns.expect(pb_nl_filter_model, validate=False)
    @public_ns.marshal_with(pb_nl_status_model, as_list=True)
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
            if language_filter == "de":
                query = query.filter(
                    Nightline.status.name.in_(["german", "german-english"]))
            elif language_filter == "en":
                query = query.filter(
                    Nightline.status.name.in_(["english", "german-english"]))

        if now_filter:
            query = query.filter(
                Nightline.now == (
                    now_filter.lower() == "true"))

        # Fetch the filtered nightlines
        nightlines = query.all()

        response = [{**nightline.status.__dict__, "now": nightline.now}
                    for nightline in nightlines]
        return response, 200
