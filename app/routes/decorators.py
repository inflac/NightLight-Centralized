from functools import wraps
from typing import Any, Callable, TypeVar, Union

from flask import request

from app.config import Config
from app.logger import logger
from app.models import Nightline

R = TypeVar("R")


def sanitize_nightline_name(f: Callable[..., R]) -> Callable[..., R]:
    @wraps(f)
    def decorated_function(self: Any, nightline_name: str, *args: Any, **kwargs: Any) -> R:
        sanitized_name = nightline_name.strip().lower()

        if not sanitized_name.isalnum() or len(sanitized_name) > 50:
            logger.debug(f"Route was called with an invalid name: '{nightline_name}'")
            return {"message": "Invalid name format"}, 400  # type: ignore

        logger.debug(f"Name used in route was sanitized to: '{sanitized_name}'")

        return f(self, sanitized_name, *args, **kwargs)

    return decorated_function


def require_admin_key(f: Callable[..., R]) -> Callable[..., Union[R, tuple[dict[str, str], int]]]:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Union[R, tuple[dict[str, str], int]]:
        api_key = request.headers.get("Authorization")
        if not api_key:
            return {"message": "Missing Authorization header"}, 401

        if api_key != Config.ADMIN_API_KEY:
            return {"message": "Admin API key required"}, 403

        return f(*args, **kwargs)

    return wrapper


def require_api_key(f: Callable[..., R]) -> Callable[..., Union[R, tuple[dict[str, str], int]]]:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Union[R, tuple[dict[str, str], int]]:
        api_key = request.headers.get("Authorization")
        if not api_key:
            return {"message": "Missing Authorization header"}, 401

        # Allow admin key to bypass nightline check
        if api_key == Config.ADMIN_API_KEY:
            return f(*args, **kwargs)

        # Attempt to extract nightline_name from keyword args
        nightline_name = kwargs.get("nightline_name")

        # Try fallback: look in positional args if not passed via kwargs
        if not nightline_name and len(args) >= 2:
            nightline_name = args[1]  # assuming method(self, nightline_name, ...)

        if not nightline_name:
            return {"message": "Nightline name not found in request"}, 400

        nightline = Nightline.get_nightline(nightline_name)
        if nightline and api_key == nightline.get_api_key().key:
            return f(*args, **kwargs)

        return {"message": "Invalid API key"}, 403

    return wrapper
