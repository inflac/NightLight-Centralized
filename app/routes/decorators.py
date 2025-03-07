from functools import wraps

def sanitize_name(f):
    """Decorator to sanitize the 'name' parameter in Flask routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        name = kwargs.get("name", "").strip().lower()
        if not name.isalnum():  # only allow alphanumeric names
            return {"error": "Invalid name format"}, 400
        kwargs["name"] = name
        return f(*args, **kwargs)
    return decorated_function