from flask_restx import fields


# API model for a single status
status_model = {
    "name": fields.String(required=True, description="Name of the status"),
    "description_de": fields.String(required=True, description="German description"),
    "description_en": fields.String(required=True, description="English description"),
    "description_now_de": fields.String(required=True, description="German description for now"),
    "description_now_en": fields.String(required=True, description="English description for now"),
}

# API model for nightline status
nightline_status_model = {
    "name": fields.String(required=True, description="Name of the status"),
    "description_de": fields.String(required=True, description="German description"),
    "description_en": fields.String(required=True, description="English description"),
    "description_now_de": fields.String(required=True, description="German description for now"),
    "description_now_en": fields.String(required=True, description="English description for now"),
    "now": fields.Boolean(required=True, description="Indicates whether the shift is currently active."),
}

# API model for the now value of a nightline
nightline_now_model = {
    'now': fields.Boolean(required=True, description="'Now' boolean status of the nightline"),
}
