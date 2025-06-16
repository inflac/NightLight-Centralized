from functools import wraps
from typing import Any, Callable, TypeVar

from app.logger import logger

R = TypeVar("R")


def sanitize_name(f: Callable[..., R]) -> Callable[..., R]:
    @wraps(f)
    def decorated_function(self: Any, name: str, *args: Any, **kwargs: Any) -> R:
        sanitized_name = name.strip().lower()

        if not sanitized_name.isalnum() or len(sanitized_name) > 15:
            logger.debug(f"Route was called with an invalid name: '{name}'")
            return {"message": "Invalid name format"}, 400  # type: ignore

        logger.debug(f"Name used in route was sanitized to: '{sanitized_name}'")

        return f(self, sanitized_name, *args, **kwargs)

    return decorated_function
