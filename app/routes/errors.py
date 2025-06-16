# error_handlers.py
from typing import Tuple

from flask import Response, jsonify
from werkzeug.exceptions import HTTPException


def internal_error(error: HTTPException) -> Tuple[Response, int]:
    """Handle 500 error (Internal Server Error)"""
    return jsonify({"message": "Internal server error"}), 500


def handle_runtime_error(error: HTTPException) -> Tuple[Response, int]:
    """Handle 500 error (Internal Server Error) for RuntimeError"""
    return jsonify({"message": "An error occured while processing data"}), 500


def handle_generic_error(error: HTTPException) -> Tuple[Response, int]:
    """Handle generic errors (Exception)"""
    return jsonify({"message": "An unexpected error occurred"}), 500
