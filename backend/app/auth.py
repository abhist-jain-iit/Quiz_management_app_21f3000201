from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from functools import wraps
from .models.user import User, Role
from .database import db

def admin_required():
    # Decorator to require admin role 
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if current_user_id:
                user = User.query.get(int(current_user_id))
                if not user or not user.is_admin():
                    return {"error": "Admin access required"}, 403
            else:
                return {"error": "Authentication required"}, 401
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def user_required():
    # Decorator to require user role 
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if current_user_id:
                user = User.query.get(int(current_user_id))
                if not user or not user.is_active:
                    return {"error": "User access required"}, 403
            else:
                return {"error": "Authentication required"}, 401
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def authenticate_user(username, password):
    """Authenticate user and return user object if valid"""
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password) and user.is_active:
        return user
    return None

def create_tokens(user):
    """Create access and refresh tokens for user"""
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return access_token, refresh_token

def init_admin_user():
    """Initialize admin user and roles if they don't exist"""
    # Create roles if they don't exist
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator role')
        db.session.add(admin_role)
    
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Regular user role')
        db.session.add(user_role)
    
    db.session.commit()
    
    # Create admin user if it doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@quizmaster.com',
            full_name='Quiz Master Admin',
            qualification='Administrator'
        )
        admin_user.set_password('Admin@123')  # Updated password
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created with username: admin, password: Admin@123")
    
    return admin_user 