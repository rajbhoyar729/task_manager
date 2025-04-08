import logging
import uuid
from flask import Flask, g
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config
from app.utils.exceptions import CustomException

mongo = PyMongo()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        # Use request ID from Flask's g object or generate a default
        record.request_id = getattr(g, 'request_id', 'no-request')
        return True

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Configure logging with request ID
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(request_id)s] - %(message)s'
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    
    app.logger.handlers = []
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Add request ID to each request
    @app.before_request
    def set_request_id():
        g.request_id = str(uuid.uuid4())

    # Global error handler
    @app.errorhandler(Exception)
    def handle_global_error(error):
        # Preserve original exception attributes
        if isinstance(error, CustomException):
            return jsonify({
                'error': error.message,
                'status_code': error.status_code,
                'request_id': getattr(g, 'request_id', 'no-request')
            }), error.status_code

        # Generic server error response
        app.logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'status_code': 500,
            'request_id': getattr(g, 'request_id', 'no-request')
        }), 500

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(tasks_bp, url_prefix='/api')

    return app