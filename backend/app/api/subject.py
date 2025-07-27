from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Subject
from ..auth import admin_required

class SubjectApi(Resource):
    def get(self, subject_id=None):
        """Get all subjects or specific subject"""
        if subject_id:
            subject = Subject.query.get(subject_id)
            if subject:
                return subject.convert_to_json(), 200
            return {'message': 'Subject does not exist.'}, 404

        search_query = request.args.get('search', '').strip()
        
        if search_query:
            subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
        else:
            subjects = Subject.query.all()
        
        subject_list = []
        for subject in subjects:
            subject_list.append(subject.convert_to_json())
        return subject_list, 200

    @jwt_required()
    @admin_required()
    def post(self):
        """Create new subject (Admin only)"""
        data = request.get_json()
        
        if not (data.get('name') and data.get('description')):
            return {'message': 'Bad request! Name and description are required.'}, 400
        
        if len(data.get('name').strip()) < 3 or len(data.get('name').strip()) > 100:
            return {'message': 'Length of name should be between 3 and 100 characters'}, 400
        
        if len(data.get('description', '').strip()) > 1000:
            return {'message': 'Description too long (max 1000 characters)'}, 400
        
        # Check if subject already exists
        existing_subject = Subject.query.filter_by(name=data.get('name').strip()).first()
        if existing_subject:
            return {"message": "Subject already exists."}, 409
        
        new_subject = Subject(
            name=data.get('name').strip(),
            description=data.get('description').strip()
        )
        
        db.session.add(new_subject)
        db.session.commit()
        
        return new_subject.convert_to_json(), 201

    @jwt_required()
    @admin_required()
    def put(self, subject_id):
        """Update subject (Admin only)"""
        data = request.get_json()
        
        if not (data.get('name') and data.get('description')):
            return {'message': 'Bad request! Name and description are required.'}, 400
        
        if len(data.get('name').strip()) < 3 or len(data.get('name').strip()) > 100:
            return {'message': 'Length of name should be between 3 and 100 characters'}, 400
        
        if len(data.get('description', '').strip()) > 1000:
            return {'message': 'Description too long (max 1000 characters)'}, 400
        
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject does not exist.'}, 404
        
        # Check if name already exists (excluding current subject)
        existing_subject = Subject.query.filter_by(name=data.get('name').strip()).first()
        if existing_subject and existing_subject.id != subject_id:
            return {"message": "Subject name already exists."}, 409
        
        subject.name = data.get('name').strip()
        subject.description = data.get('description').strip()
        
        db.session.commit()
        
        return subject.convert_to_json(), 200

    @jwt_required()
    @admin_required()
    def delete(self, subject_id):
        """Delete subject (Admin only)"""
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject does not exist.'}, 404
        
        # Check if subject has chapters
        if subject.chapters.count() > 0:
            return {'message': 'Cannot delete subject with existing chapters.'}, 400
        
        db.session.delete(subject)
        db.session.commit()
        
        return {'message': 'Subject deleted successfully.'}, 200 