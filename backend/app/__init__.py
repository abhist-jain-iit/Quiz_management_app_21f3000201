from flask import Flask
from flask_security import Security
from .database import db
from .user_datastore import user_datastore
from .models import *
from .config import config_dict

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    db.init_app(app)
    security = Security(app, user_datastore)

    return app
