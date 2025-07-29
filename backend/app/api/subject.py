from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Subject, Chapter, Quiz, Question, Score
from ..auth import admin_required

class SubjectApi(Resource):
    def get(self, subject_id=None):
        """Get all subjects or specific subject"""
        try:
            cache = current_app.cache

            if subject_id:
                # Cache individual subject for 15 minutes
                cache_key = f"subject_{subject_id}"
                try:
                    cached_subject = cache.get(cache_key)
                    if cached_subject:
                        return cached_subject, 200
                except Exception as e:
                    print(f"Cache get error: {e}")

                subject = Subject.query.get(subject_id)
                if subject:
                    subject_data = subject.convert_to_json()
                    try:
                        cache.set(cache_key, subject_data, timeout=900)
                    except Exception as e:
                        print(f"Cache set error: {e}")
                    return subject_data, 200
                return {'message': 'Subject does not exist.'}, 404

            search_query = request.args.get('search', '').strip()
            bypass_cache = request.args.get('_t') is not None
            cache_key = f"subjects_list_{search_query}"

            # Try to get from cache first (unless bypassing)
            if not bypass_cache:
                try:
                    cached_list = cache.get(cache_key)
                    if cached_list:
                        return cached_list, 200
                except Exception as e:
                    print(f"Cache get error: {e}")

            if search_query:
                subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
            else:
                subjects = Subject.query.all()

            subject_list = []
            for subject in subjects:
                # Force fresh data by refreshing the object
                db.session.refresh(subject)
                subject_list.append(subject.convert_to_json())

            # Cache subject list for 10 minutes (unless bypassing)
            if not bypass_cache:
                try:
                    cache.set(cache_key, subject_list, timeout=600)
                except Exception as e:
                    print(f"Cache set error: {e}")

            return subject_list, 200

        except Exception as e:
            print(f"Subject API error: {e}")
            return {'message': 'Internal server error'}, 500

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
        
        try:
            new_subject = Subject(
                name=data.get('name').strip(),
                description=data.get('description').strip()
            )

            db.session.add(new_subject)
            db.session.commit()

            # Invalidate caches
            try:
                cache = current_app.cache
                cache.clear()  # Simple approach - clear all cache
            except Exception as e:
                print(f"Cache clear error: {e}")

            return new_subject.convert_to_json(), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error creating subject: {e}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error creating subject: {str(e)}'}, 500

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
        
        try:
            subject.name = data.get('name').strip()
            subject.description = data.get('description').strip()

            db.session.commit()

            # Invalidate caches
            try:
                cache = current_app.cache
                cache.clear()  # Clear all cache to be safe
            except Exception as e:
                print(f"Cache clear error: {e}")

            return subject.convert_to_json(), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error updating subject: {e}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error updating subject: {str(e)}'}, 500

    @jwt_required()
    @admin_required()
    def delete(self, subject_id):
        """Delete subject and all associated data (Admin only)"""
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject does not exist.'}, 404

        try:
            # Count what will be deleted for confirmation message
            total_chapters = subject.chapters.count()
            total_quizzes = 0
            total_questions = 0
            total_scores = 0

            # Count all nested items before deletion
            for chapter in subject.chapters:
                chapter_quizzes = chapter.quizzes.count()
                total_quizzes += chapter_quizzes

                for quiz in chapter.quizzes:
                    total_questions += quiz.questions.count()
                    total_scores += quiz.scores.count()

            subject_name = subject.name

            # Delete the subject - cascade should handle the rest
            db.session.delete(subject)
            db.session.commit()

            # Invalidate caches
            try:
                cache = current_app.cache
                cache.clear()
            except Exception as e:
                print(f"Cache clear error: {e}")

            return {
                'message': f'Subject "{subject_name}" deleted successfully along with {total_chapters} chapters, {total_quizzes} quizzes, {total_questions} questions, and {total_scores} quiz attempts.'
            }, 200

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting subject: {e}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error occurred while deleting subject: {str(e)}'}, 500