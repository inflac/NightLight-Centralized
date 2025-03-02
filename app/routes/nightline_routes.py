from flask import Blueprint, jsonify, request
from ..models import Nightline

nightline_bp = Blueprint("nightline", __name__)

#TODO move this route to admin routes and rename it. Also add a route here to only fetch the status of a nl
# Route to get a specific nightline by name
@nightline_bp.route("/<string:name>", methods=["GET"])
def get_nightline(name):
    """Retrieve details of a specific nightline."""
    nightline = Nightline.get_nightline(name)

    return jsonify({
        "name": nightline.name,
        "status": nightline.status.name,  # Only return status name
        "instagram_media_id": nightline.instagram_media_id
    }), 200

# Route to update the status of a nightline
#TODO