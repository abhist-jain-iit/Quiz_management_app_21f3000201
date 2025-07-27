from flask_restful import Api
from .auth import LoginApi, RegisterApi, RefreshApi, LogoutApi, ProfileApi
from .subject import SubjectApi
from .chapter import ChapterApi
from .quiz import QuizApi
from .question import QuestionApi
from .score import ScoreApi, QuizAttemptApi
from .user import UserApi
from .search import SearchApi
from .dashboard import DashboardApi

def init_api(app):
    """Initialize API routes"""
    api = Api(app, prefix='/api')
    
    # Authentication routes
    api.add_resource(LoginApi, '/auth/login')
    api.add_resource(RegisterApi, '/auth/register')
    api.add_resource(RefreshApi, '/auth/refresh')
    api.add_resource(LogoutApi, '/auth/logout')
    api.add_resource(ProfileApi, '/auth/profile')
    
    # Subject routes
    api.add_resource(SubjectApi, '/subjects', '/subjects/<int:subject_id>')
    
    # Chapter routes
    api.add_resource(ChapterApi, '/chapters', '/chapters/<int:chapter_id>')
    
    # Quiz routes
    api.add_resource(QuizApi, '/quizzes', '/quizzes/<int:quiz_id>')
    
    # Question routes
    api.add_resource(QuestionApi, '/questions', '/questions/<int:question_id>')
    
    # Score and quiz attempt routes
    api.add_resource(ScoreApi, '/scores', '/scores/<int:score_id>')
    api.add_resource(QuizAttemptApi, '/quiz-attempt/<int:quiz_id>')
    
    # User management routes (Admin only)
    api.add_resource(UserApi, '/users', '/users/<int:user_id>')
    
    # Search routes (Admin only)
    api.add_resource(SearchApi, '/search')
    
    # Dashboard route
    api.add_resource(DashboardApi, '/dashboard')
    
    return api 