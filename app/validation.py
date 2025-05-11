from flask_restx import abort
from PIL import Image


def validate_request_body(data: dict, keys: list) -> bool:
    if not keys:
        return False
    
    missing = False
    error_msg = "Missing"
    for i, key in enumerate(keys):
        if not data or key not in data:
            missing = True
            error_msg += f" '{key}'"
            if i < (len(keys) - 1):
                error_msg += " or "
    error_msg += " in request"

    if missing:
        abort(400, error_msg)
    return True

def validate_filters(status_filter: str = None, language_filter: str = None, now_filter: str = None) -> None:
    # Validate status filter
    if status_filter:
        if ((not isinstance(status_filter, str)) or (len(status_filter) > 15) or (not status_filter.isalnum())):
            abort(400, message=f"Invalid value for status filter. Only valid status names are allowed")

    # Validate language filter
    if language_filter:
        if language_filter not in ["en", "de"]:
            abort(400, meessage=f"Invalid value for language filter. Only 'en' or 'de' are allowed")
    
    # Validate now filter
    if now_filter:
        if not now_filter in ["true", "false"]:
            abort(400, message="Invalid value for 'now' filter. Use 'true' or 'false'")

def validate_status_value(status_value: str) -> None:
    if not isinstance(status_value, str) or not status_value.strip() or len(
        status_value) > 15:
        abort(400, "'status' must be a non-empty valid status name")

def validate_instagram_credentials(username: str, password: str) -> None:
    if len(username) > 50 or len(password) > 100:
        abort(400, "Invalid 'username' or 'password' in request")

# TODO add type for image_file
def validate_image(image_file) -> None:
    # Validate image content type
    if not image_file or image_file.mimetype not in ['image/jpeg', 'image/png', 'image/gif']:
        abort(400, "Unsupported image type")

    # Validate image files content
    try:
        img = Image.open(image_file)
        img.verify()  # Verify that it's a valid image
    except Exception:
        abort(400, "Invalid image content")