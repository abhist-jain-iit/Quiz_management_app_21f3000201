from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models import db, User, Subject, Chapter, Quiz, Score
from ..auth import admin_required

class QuizApi(Resource):
    def get(self, quiz_id=None):
        try:
            if quiz_id:
                quiz = Quiz.query.get(quiz_id)
                if quiz:
                    return quiz.convert_to_json(), 200
                return {'message': 'Quiz not found'}, 404

            search_query = request.args.get('search', '').strip()
            chapter_id = request.args.get('chapter_id', '')
            is_active = request.args.get('is_active', '')

            query = Quiz.query

            if search_query:
                query = query.filter(Quiz.title.ilike(f"%{search_query}%"))

            if chapter_id:
                query = query.filter_by(chapter_id=chapter_id)

            if is_active:
                query = query.filter_by(is_active=is_active.lower() == 'true')

            quizzes = query.all()
            quiz_list = [quiz.convert_to_json() for quiz in quizzes]
            return quiz_list, 200

        except Exception as e:
            return {'message': 'Internal server error'}, 500

    @jwt_required()
    @admin_required()
    def post(self):
        data = request.get_json()

        required_fields = ['title', 'chapter_id', 'date_of_quiz', 'time_duration', 'remarks']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'{field} is required'}, 400

        title = data.get('title').strip()
        if len(title) < 3 or len(title) > 200:
            return {'message': 'Title must be 3-200 characters'}, 400

        chapter = Chapter.query.get(data.get('chapter_id'))
        if not chapter:
            return {'message': 'Chapter not found'}, 400

        try:
            quiz_date = datetime.strptime(data.get('date_of_quiz'), '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400
        time_duration = data.get('time_duration').strip()
        if ':' not in time_duration:
            return {'message': 'Invalid time format. Use HH:MM'}, 400

        try:
            new_quiz = Quiz(
                title=title,
                chapter_id=data.get('chapter_id'),
                date_of_quiz=quiz_date,
                time_duration=time_duration,
                remarks=data.get('remarks', '').strip(),
                is_active=data.get('is_active', True)
            )

            db.session.add(new_quiz)
            db.session.commit()
            return new_quiz.convert_to_json(), 201

        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating quiz: {str(e)}'}, 500

    @jwt_required()
    @admin_required()
    def put(self, quiz_id):
        data = request.get_json()
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        required_fields = ['title', 'chapter_id', 'date_of_quiz', 'time_duration', 'remarks']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'{field} is required'}, 400

        title = data.get('title').strip()
        if len(title) < 3 or len(title) > 200:
            return {'message': 'Title must be 3-200 characters'}, 400

        chapter = Chapter.query.get(data.get('chapter_id'))
        if not chapter:
            return {'message': 'Chapter not found'}, 400

        try:
            quiz_date = datetime.strptime(data.get('date_of_quiz'), '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400

        try:
            quiz.title = title
            quiz.chapter_id = data.get('chapter_id')
            quiz.date_of_quiz = quiz_date
            quiz.time_duration = data.get('time_duration').strip()
            quiz.remarks = data.get('remarks', '').strip()
            quiz.is_active = data.get('is_active', quiz.is_active)

            db.session.commit()
            return quiz.convert_to_json(), 200

        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating quiz: {str(e)}'}, 500

    @jwt_required()
    @admin_required()
    def delete(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        try:
            quiz_title = quiz.title
            db.session.delete(quiz)
            db.session.commit()
            return {'message': f'Quiz "{quiz_title}" deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting quiz'}, 500