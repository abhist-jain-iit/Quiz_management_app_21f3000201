from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ..models import db, User, Role
from ..auth import authenticate_user, create_tokens

class LoginApi(Resource):
    def post(self):
        """User login endpoint"""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return {'message': 'Username and password required'}, 400
        
        user = authenticate_user(data['username'], data['password'])
        
        if not user:
            return {'message': 'Invalid credentials'}, 401
        
        access_token, refresh_token = create_tokens(user)
        
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.convert_to_json()
        }, 200

class RegisterApi(Resource):
    def post(self):
        """User registration endpoint"""
        data = request.get_json()
        
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'{field} is required'}, 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 409
        
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 409
        
        # Convert date_of_birth string to Date object if provided
        date_of_birth = None
        if data.get('date_of_birth'):
            try:
                from datetime import datetime
                date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            qualification=data.get('qualification'),
            date_of_birth=date_of_birth
        )
        user.set_password(data['password'])
        
        # Assign user role
        user_role = Role.query.filter_by(name='user').first()
        if user_role:
            user.roles.append(user_role)
        
        db.session.add(user)
        db.session.commit()
        
        # Create tokens for the new user
        access_token, refresh_token = create_tokens(user)
        
        return {
            'message': 'Registration successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.convert_to_json()
        }, 201

class RefreshApi(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return {'message': 'Invalid user'}, 401
        
        access_token = create_access_token(identity=current_user_id)
        
        return {
            'access_token': access_token
        }, 200

class LogoutApi(Resource):
    @jwt_required()
    def post(self):
        """Logout endpoint (client should discard tokens)"""
        return {'message': 'Logout successful'}, 200

class ProfileApi(Resource):
    @jwt_required()
    def get(self):
        """Get current user profile"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        return {
            'user': user.convert_to_json()
        }, 200 