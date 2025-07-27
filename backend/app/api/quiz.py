from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, time
from ..models import db, User, Subject, Chapter, Quiz
from ..auth import admin_required

class QuizApi(Resource):
    def get(self, quiz_id=None):
        """Get all quizzes or specific quiz"""
        if quiz_id:
            quiz = Quiz.query.get(quiz_id)
            if quiz:
                return quiz.convert_to_json(), 200
            return {'message': 'Quiz does not exist.'}, 404

        search_query = request.args.get('search', '').strip()
        chapter_id = request.args.get('chapter_id')
        is_active = request.args.get('is_active')

        if search_query:
            quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{search_query}%"))
        else:
            quizzes = Quiz.query
        
        if chapter_id:
            quizzes = quizzes.filter_by(chapter_id=chapter_id)
        
        if is_active is not None:
            quizzes = quizzes.filter_by(is_active=is_active.lower() == 'true')
        
        quizzes = quizzes.all()
        
        quiz_list = []
        for quiz in quizzes:
            quiz_list.append(quiz.convert_to_json())
        return quiz_list, 200

    @jwt_required()
    @admin_required()
    def post(self):
        """Create new quiz (Admin only)"""
        data = request.get_json()
        
        required_fields = ['title', 'chapter_id', 'date_of_quiz', 'time_duration', 'remarks']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'Bad request! {field} is required.'}, 400
        
        if len(data.get('title').strip()) < 3 or len(data.get('title').strip()) > 200:
            return {'message': 'Length of title should be between 3 and 200 characters'}, 400
        
        # Check if chapter exists
        chapter = Chapter.query.get(data.get('chapter_id'))
        if not chapter:
            return {'message': 'Chapter not found'}, 400
        
        # Parse date
        try:
            quiz_date = datetime.strptime(data.get('date_of_quiz'), '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400
        
        # Parse time duration
        try:
            time_parts = data.get('time_duration').split(':')
            if len(time_parts) != 2:
                return {'message': 'Invalid time format. Use HH:MM'}, 400
            hours, minutes = int(time_parts[0]), int(time_parts[1])
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                return {'message': 'Invalid time values'}, 400
            duration = time(hours, minutes)
        except (ValueError, IndexError):
            return {'message': 'Invalid time format. Use HH:MM'}, 400
        
        new_quiz = Quiz(
            title=data.get('title').strip(),
            chapter_id=data.get('chapter_id'),
            date_of_quiz=quiz_date,
            time_duration=duration,
            remarks=data.get('remarks', '').strip(),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        return new_quiz.convert_to_json(), 201

    @jwt_required()
    @admin_required()
    def put(self, quiz_id):
        """Update quiz (Admin only)"""
        data = request.get_json()
        
        required_fields = ['title', 'chapter_id', 'date_of_quiz', 'time_duration', 'remarks']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'Bad request! {field} is required.'}, 400
        
        if len(data.get('title').strip()) < 3 or len(data.get('title').strip()) > 200:
            return {'message': 'Length of title should be between 3 and 200 characters'}, 400
        
        # Check if chapter exists
        chapter = Chapter.query.get(data.get('chapter_id'))
        if not chapter:
            return {'message': 'Chapter not found'}, 400
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz does not exist.'}, 404
        
        # Parse date
        try:
            quiz_date = datetime.strptime(data.get('date_of_quiz'), '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400
        
        # Parse time duration
        try:
            time_parts = data.get('time_duration').split(':')
            if len(time_parts) != 2:
                return {'message': 'Invalid time format. Use HH:MM'}, 400
            hours, minutes = int(time_parts[0]), int(time_parts[1])
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                return {'message': 'Invalid time values'}, 400
            duration = time(hours, minutes)
        except (ValueError, IndexError):
            return {'message': 'Invalid time format. Use HH:MM'}, 400
        
        quiz.title = data.get('title').strip()
        quiz.chapter_id = data.get('chapter_id')
        quiz.date_of_quiz = quiz_date
        quiz.time_duration = duration
        quiz.remarks = data.get('remarks', '').strip()
        quiz.is_active = data.get('is_active', quiz.is_active)
        
        db.session.commit()
        
        return quiz.convert_to_json(), 200

    @jwt_required()
    @admin_required()
    def delete(self, quiz_id):
        """Delete quiz (Admin only)"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz does not exist.'}, 404
        
        # Check if quiz has questions
        if quiz.questions.count() > 0:
            return {'message': 'Cannot delete quiz with existing questions.'}, 400
        
        # Check if quiz has scores
        if quiz.scores.count() > 0:
            return {'message': 'Cannot delete quiz with existing scores.'}, 400
        
        db.session.delete(quiz)
        db.session.commit()
        
        return {'message': 'Quiz deleted successfully.'}, 200 