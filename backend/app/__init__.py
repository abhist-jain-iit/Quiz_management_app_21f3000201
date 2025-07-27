from flask import Flask
from flask_jwt_extended import JWTManager
from .database import db
from .models import *
from .config import config_dict
from .auth import init_admin_user

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Initialize database and create admin user
    with app.app_context():
        db.create_all()
        init_admin_user()
    
    return app
