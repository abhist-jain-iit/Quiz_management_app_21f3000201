from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Subject, Chapter, Quiz, Question, Score
from ..auth import admin_required

class ChapterApi(Resource):
    def get(self, chapter_id=None):
        """Get all chapters or specific chapter"""
        cache = current_app.cache
        if chapter_id:
            chapter = Chapter.query.get(chapter_id)
            if chapter:
                return chapter.convert_to_json(), 200
            return {'message': 'Chapter does not exist.'}, 404

        search_query = request.args.get('search', '').strip()
        subject_id = request.args.get('subject_id')

        if search_query:
            chapters = Chapter.query.filter(Chapter.name.ilike(f"%{search_query}%"))
        else:
            chapters = Chapter.query
        
        if subject_id:
            chapters = chapters.filter_by(subject_id=subject_id)
        
        chapters = chapters.all()
        
        chapter_list = []
        for chapter in chapters:
            chapter_list.append(chapter.convert_to_json())
        return chapter_list, 200

    @jwt_required()
    @admin_required()
    def post(self):
        """Create new chapter (Admin only)"""
        data = request.get_json()
        
        if not (data.get('name') and data.get('description') and data.get('subject_id')):
            return {'message': 'Bad request! Name, description, and subject_id are required.'}, 400
        
        if len(data.get('name').strip()) < 3 or len(data.get('name').strip()) > 100:
            return {'message': 'Length of name should be between 3 and 100 characters'}, 400
        
        if len(data.get('description', '').strip()) > 1000:
            return {'message': 'Description too long (max 1000 characters)'}, 400
        
        # Check if subject exists
        subject = Subject.query.get(data.get('subject_id'))
        if not subject:
            return {'message': 'Subject not found'}, 400
        
        # Check if chapter already exists in this subject
        existing_chapter = Chapter.query.filter_by(
            name=data.get('name').strip(),
            subject_id=data.get('subject_id')
        ).first()
        
        if existing_chapter:
            return {"message": "Chapter already exists in this subject."}, 409
        
        try:
            new_chapter = Chapter(
                name=data.get('name').strip(),
                description=data.get('description').strip(),
                subject_id=data.get('subject_id')
            )

            db.session.add(new_chapter)
            db.session.commit()

            # Clear cache safely
            try:
                cache = current_app.cache
                cache.clear()
            except Exception as cache_error:
                print(f"Cache clear error: {cache_error}")

            return new_chapter.convert_to_json(), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error creating chapter: {e}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error creating chapter: {str(e)}'}, 500

    @jwt_required()
    @admin_required()
    def put(self, chapter_id):
        """Update chapter (Admin only)"""
        data = request.get_json()
        
        if not (data.get('name') and data.get('description') and data.get('subject_id')):
            return {'message': 'Bad request! Name, description, and subject_id are required.'}, 400
        
        if len(data.get('name').strip()) < 3 or len(data.get('name').strip()) > 100:
            return {'message': 'Length of name should be between 3 and 100 characters'}, 400
        
        if len(data.get('description', '').strip()) > 1000:
            return {'message': 'Description too long (max 1000 characters)'}, 400
        
        # Check if subject exists
        subject = Subject.query.get(data.get('subject_id'))
        if not subject:
            return {'message': 'Subject not found'}, 400
        
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return {'message': 'Chapter does not exist.'}, 404
        
        # Check if chapter name already exists in this subject (excluding current chapter)
        existing_chapter = Chapter.query.filter_by(
            name=data.get('name').strip(),
            subject_id=data.get('subject_id')
        ).first()
        
        if existing_chapter and existing_chapter.id != chapter_id:
            return {"message": "Chapter name already exists in this subject."}, 409
        
        try:
            chapter.name = data.get('name').strip()
            chapter.description = data.get('description').strip()
            chapter.subject_id = data.get('subject_id')

            db.session.commit()

            # Clear cache safely
            try:
                cache = current_app.cache
                cache.clear()
            except Exception as cache_error:
                print(f"Cache clear error: {cache_error}")

            return chapter.convert_to_json(), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error updating chapter: {e}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error updating chapter: {str(e)}'}, 500

    @jwt_required()
    @admin_required()
    def delete(self, chapter_id):
        """Delete chapter and all associated data (Admin only)"""
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return {'message': 'Chapter does not exist.'}, 404

        try:
            # Count what will be deleted for confirmation message
            total_quizzes = chapter.quizzes.count()
            total_questions = 0
            total_scores = 0

            # Count all nested items before deletion
            for quiz in chapter.quizzes:
                total_questions += quiz.questions.count()
                total_scores += quiz.scores.count()

            chapter_name = chapter.name

            # Delete the chapter - cascade should handle the rest
            db.session.delete(chapter)
            db.session.commit()

            # Invalidate caches
            try:
                cache = current_app.cache
                cache.clear()
            except Exception as e:
                print(f"Cache clear error: {e}")

            return {
                'message': f'Chapter "{chapter_name}" deleted successfully along with {total_quizzes} quizzes, {total_questions} questions, and {total_scores} quiz attempts.'
            }, 200

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting chapter: {e}")
            return {'message': 'Error occurred while deleting chapter.'}, 500