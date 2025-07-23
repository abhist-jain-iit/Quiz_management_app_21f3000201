from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel
from app.database import db

# UserMixin adds basic login-related features automatically. we dont have to write them separately.
# Like checking if the user is logged in or getting the user's ID

class User(BaseModel, UserMixin):
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(60), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(100), nullable=False, default='user')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    scores = db.relationship("Score", backref="user", cascade="all, delete-orphan", lazy=True)
        # backref and back_populates: They are used in SQLAlchemy to link two tables together.
        # Use **backref** when you want quick setup.
        # Use **back_populates** when you want more control or when customizing both sides of the relationship.

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def convert_to_json(self):
        return {
            'id': self.id,
            'name': self.full_name,
            'email': self.email,
            'qualification': self.qualification,
            'dob': self.dob.strftime('%Y-%m-%d') if self.dob else None,
            'role': self.role,
            'is_admin': self.is_admin
        }