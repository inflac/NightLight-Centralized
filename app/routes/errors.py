# error_handlers.py
from flask import jsonify


def internal_error(error):
    """Handle 500 error (Internal Server Error)"""
    return jsonify({"message": "Internal server error"}), 500


def handle_runtime_error(error):
    """Handle 500 error (Internal Server Error) for RuntimeError"""
    return jsonify({"message": "An error occured while processing data"}), 500


def handle_generic_error(error):
    """Handle generic errors (Exception)"""
    return jsonify({"message": "An unexpected error occurred"}), 500
