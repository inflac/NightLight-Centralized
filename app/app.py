from setup import create_app
from config import Config

app = create_app()

# Register the blueprint for status-related routes
from routes import *

app.register_blueprint(status_bp, url_prefix='/status')
app.register_blueprint(city_bp, url_prefix='/city')

# Global error handlers
app.register_error_handler(400, bad_request_error)
app.register_error_handler(404, not_found_error)
app.register_error_handler(500, internal_error)
app.register_error_handler(ValueError, handle_value_error)
app.register_error_handler(RuntimeError, handle_runtime_error)
app.register_error_handler(Exception, handle_generic_error)

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=True)
