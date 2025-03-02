from flask import Blueprint, jsonify, request
from ..models import Nightline

public_bp = Blueprint("public", __name__)

# Route to get the status of a nightline
@public_bp.route("/<string:name>/status", methods=["GET"])
def get_status(name):
    """Retrieve the status of a nightline"""
    nightline = Nightline.get_nightline(name)
    return jsonify({
        "status": nightline.status.name,
        "description_de": nightline.status.description_de,
        "description_en": nightline.status.description_en,
        "description_now_de": nightline.status.description_now_de,
        "description_now_en": nightline.status.description_now_en,
    }), 200

@public_bp.route("/nightlines/statuses", methods=["GET"])
def get_all_statuses():
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
                Nightline.status.name in [
                    "german", "german-english"])
        elif language_filter == 'en':
            query = query.filter(
                Nightline.status.name in [
                    "english", "german-english"])

    if now_filter:
        query = query.filter(Nightline.now == (now_filter.lower() == 'true'))

    # Fetch and format the results
    nightlines = query.all()
    nightline_list = [{
        "name": nightline.name,
        "status": nightline.status.name,
        "description_de": nightline.status.description_de,
        "description_en": nightline.status.description_en,
        "description_now_de": nightline.status.description_now_de,
        "description_now_en": nightline.status.description_now_en,
        "now": nightline.now,
    } for nightline in nightlines]

    return jsonify(nightline_list), 200
