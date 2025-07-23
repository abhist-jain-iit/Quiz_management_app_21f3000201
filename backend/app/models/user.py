from flask_security import UserMixin, RoleMixin
from .base import BaseModel, db

class UserRole(BaseModel):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id'),)

class Role(BaseModel, RoleMixin):
    __tablename__ = 'roles'
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    # Flask-Security-Too: users backref is set in User
    def __repr__(self):
        return f'<Role {self.name}>'

class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    fs_token_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    # Flask-Security-Too: relationship to roles
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    scores = db.relationship('Score', backref='user', lazy='dynamic')
    def __repr__(self):
        return f'<User {self.username}>'