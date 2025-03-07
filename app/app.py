from flask import Flask, Blueprint
from flask_restx import Api

from app.config import Config
from app.db import db
from app.setup import preinitialize_statuses
from app.routes import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set up logging
    logger = Config.configure_logging()

    # Configure CORS
    Config.configure_cors(app)
    logger.info("CORS configuration applied.")

    db.init_app(app)
    logger.info("Database initialized.")

    with app.app_context():
        db.create_all()
        preinitialize_statuses()

    # Create a single API instance
    api_bp = Blueprint("api", __name__)
    api = Api(
        api_bp,
        title="NightLight-Centralized API",
        version="1.0",
        description="API for managing the availability status of Nightlines",
        doc=Config.API_DOC_PATH)

    # Register public routes
    api.add_namespace(public_ns, path="/public")
    # Register nightline routes
    api.add_namespace(nightline_ns, path="/nightline")
    logger.info("Core namespaces added.")

    # Conditionally register admin routes
    if Config.ENABLE_ADMIN_ROUTES:
        api.add_namespace(admin_status_ns, path="/admin/status")
        api.add_namespace(admin_nightline_ns, path="/admin/nightline")
        logger.info("Admin namespace added.")

    # Register the API
    app.register_blueprint(api_bp)
    logger.info("API blueprint registered.")

    # Global error handlers
    app.register_error_handler(400, bad_request_error)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)
    app.register_error_handler(ValueError, handle_value_error)
    app.register_error_handler(RuntimeError, handle_runtime_error)
    app.register_error_handler(Exception, handle_generic_error)
    logger.info("Global error handlers registered.")

    return app
