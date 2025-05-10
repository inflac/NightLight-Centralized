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

def validate_status_value(status_value: str) -> None:
    if not isinstance(status_value, str) or not status_value.strip() or len(
        status_value) > 15:
        abort(400, "'status' must be a non-empty valid status name")

def validate_instagram_credentials(username: str, password: str) -> None:
    if len(username) > 50 or len(password) > 100:
        abort(400, "Invalid 'username' or 'password' in request")

def validate_image(image_file) -> None:
    # Validate image content type
    if not image_file or image_file.mimetype not in ['image/jpeg', 'image/png', 'image/gif']:
        abort(400, "Unsupported image type")

    # Validate image files content
    try:
        img = Image.open(image_file)
        img.verify()  # Verify that it's a valid image
        img.close()
    except Exception:
        abort(400, "Invalid image content")