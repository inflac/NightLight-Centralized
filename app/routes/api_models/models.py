from flask_restx import fields

# API model for errors
error_model = {
    "message": fields.String(required=True, description="Error message"),
}

success_model = {
    "message": fields.String(required=True, description="Success message"),
}

# API model for status objects
status_model = {
    "status_name": fields.String(required=True, description="Name of the status"),
    "description_de": fields.String(required=True, description="German description"),
    "description_en": fields.String(required=True, description="English description"),
    "description_now_de": fields.String(required=True, description="German description for now"),
    "description_now_en": fields.String(required=True, description="English description for now"),
}

# API model for nightline objects
nightline_model = {
    "nightline_name": fields.String(required=True, description="Name of the nightline"),
    "now": fields.Boolean(required=True, description="'Now' boolean status of the nightline"),
}

# API model for nightline statuses
nightline_status_model = {
    "nightline_name": fields.String(required=True, description="Name of the nightline"),
    "status_name": fields.String(required=True, description="Name of the status"),
    "description_de": fields.String(required=True, description="German description"),
    "description_en": fields.String(required=True, description="English description"),
    "description_now_de": fields.String(required=True, description="German description for now"),
    "description_now_en": fields.String(required=True, description="English description for now"),
    "now": fields.Boolean(required=True, description="Indicates whether the shift is currently active"),
}

admin_nightline_model = {
    "nightline_id": fields.Integer(required=True, description="ID of the nightline in the database"),
    "nightline_name": fields.String(required=True, description="Name of the nightline"),
    "status_name": fields.String(required=True, description="Name of the status"),
    "instagram_media_id": fields.String(required=True, description="ID of an Instagram post"),
    "now": fields.Boolean(required=True, description="'Now' boolean status of the nightline"),
}
