import logging
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, WrongTokenError, RevokedTokenError, FreshTokenRequired
from flask_cors import CORS
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from .database import db
from .models import *
from .config import config_dict
from .auth import init_admin_user
from .api.routes import init_api
from .default_data import create_default_data
from flask_caching import Cache
from .celery_worker import make_celery

# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Disable SQLAlchemy verbose logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    # Disable SQLAlchemy logging
    app.config['SQLALCHEMY_ECHO'] = False
    logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Initialize CORS
    CORS(app,
         origins=['http://localhost:8080', 'http://127.0.0.1:8080'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)
    
    # Initialize cache with fallback to SimpleCache if Redis is not available
    try:
        cache = Cache(app, config={
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': app.config.get('REDIS_URL', 'redis://localhost:6379/1'),
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        })
        print("✅ Redis cache initialized successfully")
    except Exception as e:
        print(f"⚠️  Redis not available, falling back to SimpleCache: {e}")
        cache = Cache(app, config={
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        })
    app.cache = cache

    # Initialize Celery
    app.celery = make_celery(app)
    
    # JWT Error Handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Missing Authorization Header"}), 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Fresh token required"}), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has been revoked"}), 401
    
    # Global error handler for JWT exceptions
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization(error):
        return jsonify({"error": "Missing Authorization Header"}), 401
    
    @app.errorhandler(InvalidHeaderError)
    def handle_invalid_header(error):
        return jsonify({"error": "Invalid Authorization Header"}), 401
    
    @app.errorhandler(WrongTokenError)
    def handle_wrong_token(error):
        return jsonify({"error": "Wrong token type"}), 401
    
    @app.errorhandler(RevokedTokenError)
    def handle_revoked_token(error):
        return jsonify({"error": "Token has been revoked"}), 401
    
    # Handle JWT decode errors and other exceptions
    @app.errorhandler(Exception)
    def handle_exception(e):
        if "jwt" in str(type(e)).lower() or "authorization" in str(e).lower() or "decode" in str(e).lower():
            return jsonify({"error": "Authentication failed"}), 401
        elif "not found" in str(e).lower():
            return jsonify({"error": "Resource not found"}), 404
        return jsonify({"error": "Internal server error"}), 500
    
    # Handle 404 errors specifically
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    # Initialize API routes
    init_api(app)
    
    # Initialize database and create admin user and default data
    with app.app_context():
        db.create_all()
        init_admin_user()

        # Create default data if enabled
        if app.config.get('CREATE_DEFAULT_DATA', True):
            create_default_data()
    
    return app
