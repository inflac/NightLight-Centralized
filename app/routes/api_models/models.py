from flask_restx import fields

# API model for errors
error_model = {
    "message": fields.String(required=True, description="Error message"),
}

success_model = {
    "message": fields.String(required=True, description="Success message"),
}

api_key_model = {
    "API-Key": fields.String(required=True, description="API-Key for the requested nightline"),
}

# API model for status objects
status_model = {
    "status_name": fields.String(required=True, description="Name of the status"),
    "description_de": fields.String(required=True, description="German description"),
    "description_en": fields.String(required=True, description="English description"),
    "description_now_de": fields.String(required=True, description="German description for now"),
    "description_now_en": fields.String(required=True, description="English description for now"),
}

set_status_model = {
    "status": fields.String(required=True, description="Name of the status"),
}

set_status_config_model = {
    "status": fields.String(required=True, description="Name of the status"),
    "instagram_story": fields.Boolean(required=True, description="'instagram_story' boolean of status 'status'"),
}


set_now_model = {
    "now": fields.Boolean(required=True, description="'Now' boolean status of the nightline"),
}

set_days_phone_model = {
    "days_phone": fields.String(required=True, description="Days the nightline is available via phone"),
}

set_days_chat_model = {
    "days_chat": fields.String(required=True, description="Days the nightline is available via chat"),
}

set_time_model = {
    "time": fields.String(required=True, description="Time the nightline is available"),
}

# API model for nightline objects
nightline_model = {
    "nightline_name": fields.String(required=True, description="Name of the nightline"),
    "now": fields.Boolean(required=True, description="'Now' boolean status of the nightline"),
    "days": fields.String(required=True, description="Days the nightline is available"),
    "time": fields.String(required=True, description="Time the nightline is available"),
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

instagram_create_model = {
    "username": fields.String(required=True, description="Username of the instagram account"),
    "password": fields.String(required=True, description="Password of the instagram account"),
}

admin_nightline_model = {
    "nightline_id": fields.Integer(required=True, description="ID of the nightline in the database"),
    "nightline_name": fields.String(required=True, description="Name of the nightline"),
    "status_name": fields.String(required=True, description="Name of the status"),
    "instagram_media_id": fields.String(required=True, description="ID of an Instagram post"),
    "now": fields.Boolean(required=True, description="'Now' boolean status of the nightline"),
    "days_phone": fields.String(required=True, description="Days the nightline is available via phone"),
    "days_chat": fields.String(required=True, description="Days the nightline is available via chat"),
    "time": fields.String(required=True, description="Time the nightline is available"),
}
