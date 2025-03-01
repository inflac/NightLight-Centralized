from flask import Flask

from time import sleep

from .config import Config
from .db import db
from .setup import preinitialize_statuses
from .routes import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set up logging
    Config.configure_logging()

    # Configure CORS
    Config.configure_cors(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        sleep(10)
        preinitialize_statuses()

    # Register blueprints
    app.register_blueprint(status_bp, url_prefix='/status')
    app.register_blueprint(city_bp, url_prefix='/city')

    # Global error handlers
    app.register_error_handler(400, bad_request_error)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)
    app.register_error_handler(ValueError, handle_value_error)
    app.register_error_handler(RuntimeError, handle_runtime_error)
    app.register_error_handler(Exception, handle_generic_error)

    return app