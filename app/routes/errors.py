# error_handlers.py
from flask import jsonify

def bad_request_error(error):
    """Handle 400 error (Bad Request)"""
    return jsonify({"error": str(error)}), 400

def not_found_error(error):
    """Handle 404 error (Not Found)"""
    return jsonify({"error": "Resource not found"}), 404

def internal_error(error):
    """Handle 500 error (Internal Server Error)"""
    return jsonify({"error": "Internal server error"}), 500

def handle_value_error(error):
    """Handle 400 error (Bad Request) for ValueError"""
    return jsonify({"error": str(error)}), 400

def handle_runtime_error(error):
    """Handle 500 error (Internal Server Error) for RuntimeError"""
    return jsonify({"error": str(error)}), 500

def handle_generic_error(error):
    """Handle generic errors (Exception)"""
    return jsonify({"error": "An unexpected error occurred"}), 500
