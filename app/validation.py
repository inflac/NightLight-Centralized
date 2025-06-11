from flask_restx import abort
from PIL import Image
from werkzeug.datastructures.file_storage import FileStorage


def validate_request_body(data: dict, keys: list) -> bool:
    """Check if keys exist in request body"""
    if not keys:
        return False

    missing = False
    error_msg = "Missing"
    for i, key in enumerate(keys):
        if not data or key not in data:
            missing = True
            error_msg += f" '{key}'"
            if i < (len(keys) - 1):
                error_msg += " or"
    error_msg += " in request"

    if missing:
        abort(400, error_msg)
        return False
    return True


def validate_filters(status_filter: str = None, language_filter: str = None, now_filter: str = None) -> None:
    """Validate the value of filter parameters"""
    if status_filter:  # Validate status filter
        if (not isinstance(status_filter, str)) or (len(status_filter) > 15) or (not status_filter.isalnum()):
            abort(
                400,
                message=f"Invalid value for status filter. Only valid status names are allowed",
            )

    if language_filter:  # Validate language filter
        if language_filter not in ["en", "de"]:
            abort(
                400,
                meessage=f"Invalid value for language filter. Only 'en' or 'de' are allowed",
            )

    if now_filter:  # Validate now filter
        if not now_filter in ["true", "false"]:
            abort(400, message="Invalid value for 'now' filter. Use 'true' or 'false'")


def validate_status_value(status_value: str) -> None:
    """Validate the format of a status parameter"""
    if not isinstance(status_value, str) or not status_value.strip() or len(status_value) > 15:
        abort(400, "'status' must be a non-empty valid status name")


def validate_instagram_credentials(username: str, password: str) -> None:
    """Validate the format of instagram credentials"""
    if len(username) > 50 or len(password) > 100:
        abort(400, "Invalid 'username' or 'password' in request")


def validate_image(image_file: FileStorage) -> None:
    """Validate an image file"""
    # Validate image content type
    if (not image_file) or (image_file.mimetype not in ["image/jpeg", "image/png", "image/gif"]):
        print(image_file.mimetype)
        abort(400, "Unsupported image type")
        return

    # Validate image files content
    try:
        img = Image.open(image_file)
        img.verify()  # Verify that it's a valid image
    except Exception:
        abort(400, "Invalid image content")
