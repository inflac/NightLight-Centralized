from functools import wraps

from app.logger import logger

def sanitize_name(f):
    @wraps(f)
    def decorated_function(self, name, *args, **kwargs):
        # Sanitize the name
        sanitized_name = name.strip().lower()

        if not sanitized_name.isalnum() or len(sanitized_name) > 15:
            logger.debug(f"Route was called with an invalid name: '{name}'")
            return {"message": "Invalid name format"}, 400

        logger.debug(
            f"Name used in route was sanitized to: '{sanitized_name}'")

        # Call the original function with the sanitized name
        return f(self, sanitized_name, *args, **kwargs)
    return decorated_function
