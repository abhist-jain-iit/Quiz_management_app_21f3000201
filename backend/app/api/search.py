from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from ..models.user import User, Role
from ..models.subject import Subject
from ..models.chapter import Chapter
from ..models.quiz import Quiz
from ..models.question import Question
from ..models.score import Score
from ..auth import admin_required

class SearchApi(Resource):
    @jwt_required()
    @admin_required()
    def get(self):
        """Comprehensive search across all entities (Admin only)"""
        search_query = request.args.get('q', '').strip()
        entity_type = request.args.get('type', '').strip()  # users, subjects, chapters, quizzes, questions
        
        if not search_query:
            return {'message': 'Search query is required'}, 400
        
        results = {}
        
        # Search users
        if not entity_type or entity_type == 'users':
            users = User.query.filter(
                (User.username.ilike(f"%{search_query}%")) |
                (User.email.ilike(f"%{search_query}%")) |
                (User.full_name.ilike(f"%{search_query}%")) |
                (User.qualification.ilike(f"%{search_query}%"))
            ).limit(10).all()
            results['users'] = [user.convert_to_json() for user in users]
        
        # Search subjects
        if not entity_type or entity_type == 'subjects':
            subjects = Subject.query.filter(
                (Subject.name.ilike(f"%{search_query}%")) |
                (Subject.description.ilike(f"%{search_query}%"))
            ).limit(10).all()
            results['subjects'] = [subject.convert_to_json() for subject in subjects]
        
        # Search chapters
        if not entity_type or entity_type == 'chapters':
            chapters = Chapter.query.filter(
                (Chapter.name.ilike(f"%{search_query}%")) |
                (Chapter.description.ilike(f"%{search_query}%"))
            ).limit(10).all()
            results['chapters'] = [chapter.convert_to_json() for chapter in chapters]
        
        # Search quizzes
        if not entity_type or entity_type == 'quizzes':
            quizzes = Quiz.query.filter(
                (Quiz.title.ilike(f"%{search_query}%")) |
                (Quiz.remarks.ilike(f"%{search_query}%"))
            ).limit(10).all()
            results['quizzes'] = [quiz.convert_to_json() for quiz in quizzes]
        
        # Search questions
        if not entity_type or entity_type == 'questions':
            questions = Question.query.filter(
                (Question.question_statement.ilike(f"%{search_query}%")) |
                (Question.option1.ilike(f"%{search_query}%")) |
                (Question.option2.ilike(f"%{search_query}%")) |
                (Question.option3.ilike(f"%{search_query}%")) |
                (Question.option4.ilike(f"%{search_query}%"))
            ).limit(10).all()
            results['questions'] = [question.convert_to_json() for question in questions]
        
        return {
            'search_query': search_query,
            'results': results,
            'total_results': sum(len(v) for v in results.values())
        }, 200 