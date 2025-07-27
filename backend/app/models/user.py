from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel, db

class UserRole(BaseModel):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id'),)

class Role(BaseModel):
    __tablename__ = 'roles'
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    def convert_to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(BaseModel):
    __tablename__ = 'users'
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    scores = db.relationship('Score', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self):
        return self.has_role('admin')
    
    def convert_to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'qualification': self.qualification,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'is_active': self.is_active,
            'roles': [role.name for role in self.roles],
            'is_admin': self.is_admin(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'