# error_handlers.py
from typing import Tuple

from flask import Response, jsonify
from werkzeug.exceptions import HTTPException


def handle_404_error(error: HTTPException) -> Tuple[Response, int]:
    """Handle 404 error (Not Found)"""
    return jsonify({"message": "Resource not found"}), 404


def handle_500_error(error: HTTPException) -> Tuple[Response, int]:
    """Handle 500 error (Internal Server Error)"""
    return jsonify({"message": "Internal server error"}), 500


def handle_runtime_error(error: RuntimeError) -> Tuple[Response, int]:
    """Handle 500 error (Internal Server Error) for RuntimeError"""
    return jsonify({"message": "An error occurred while processing data"}), 500


def handle_generic_error(error: Exception) -> Tuple[Response, int]:
    """Handle generic exceptions"""
    return jsonify({"message": "An unexpected error occurred"}), 500
