from flask_security import SQLAlchemyUserDatastore
from app.database import db
from app.models.user import User, Role
# Initialize the user datastore
user_datastore = SQLAlchemyUserDatastore(db, User, Role)