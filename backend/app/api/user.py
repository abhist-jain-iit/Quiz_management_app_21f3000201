from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User, Role
from ..database import db
from ..auth import admin_required

class UserApi(Resource):
    @jwt_required()
    @admin_required()
    def get(self, user_id=None):
        """Get all users or specific user (Admin only)"""
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.convert_to_json(), 200
            return {'message': 'User does not exist.'}, 404

        search_query = request.args.get('search', '').strip()
        role_filter = request.args.get('role', '').strip()

        if search_query:
            users = User.query.filter(
                (User.username.ilike(f"%{search_query}%")) |
                (User.email.ilike(f"%{search_query}%")) |
                (User.full_name.ilike(f"%{search_query}%"))
            )
        else:
            users = User.query
        
        if role_filter:
            users = users.join(User.roles).filter(Role.name == role_filter)
        
        users = users.all()
        
        user_list = []
        for user in users:
            user_list.append(user.convert_to_json())
        return user_list, 200

    @jwt_required()
    @admin_required()
    def put(self, user_id):
        """Update user (Admin only)"""
        data = request.get_json()
        
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User does not exist.'}, 404
        
        # Update fields if provided
        if data.get('full_name'):
            user.full_name = data.get('full_name').strip()
        
        if data.get('qualification'):
            user.qualification = data.get('qualification').strip()
        
        if data.get('is_active') is not None:
            user.is_active = data.get('is_active')
        
        if data.get('date_of_birth'):
            from datetime import datetime
            try:
                user.date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400
        
        db.session.commit()
        
        return user.convert_to_json(), 200

    @jwt_required()
    @admin_required()
    def delete(self, user_id):
        """Delete user (Admin only)"""
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User does not exist.'}, 404
        
        # Prevent admin from deleting themselves
        current_user_id = get_jwt_identity()
        if user.id == current_user_id:
            return {'message': 'Cannot delete your own account.'}, 400
        
        # Check if user has scores
        if user.scores.count() > 0:
            return {'message': 'Cannot delete user with existing scores.'}, 400
        
        db.session.delete(user)
        db.session.commit()
        
        return {'message': 'User deleted successfully.'}, 200 