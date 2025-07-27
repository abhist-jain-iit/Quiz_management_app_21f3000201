from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from ..models.user import User, Role
from ..models.subject import Subject
from ..models.chapter import Chapter
from ..models.quiz import Quiz
from ..models.question import Question
from ..models.score import Score
from ..database import db

class DashboardApi(Resource):
    @jwt_required()
    def get(self):
        """Get comprehensive dashboard data"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.is_admin():
            return self._get_admin_dashboard()
        else:
            return self._get_user_dashboard(user)
    
    def _get_admin_dashboard(self):
        """Admin dashboard with comprehensive statistics"""
        # Basic counts
        total_users = User.query.filter_by(is_active=True).count()
        total_subjects = Subject.query.count()
        total_chapters = Chapter.query.count()
        total_quizzes = Quiz.query.count()
        total_questions = Question.query.count()
        total_attempts = Score.query.count()
        
        # Recent activity
        recent_scores = Score.query.order_by(Score.time_stamp_of_attempt.desc()).limit(10).all()
        recent_scores_data = [score.convert_to_json() for score in recent_scores]
        
        # Quiz statistics
        active_quizzes = Quiz.query.filter_by(is_active=True).count()
        inactive_quizzes = Quiz.query.filter_by(is_active=False).count()
        
        # User statistics
        admin_users = User.query.join(User.roles).filter(Role.name == 'admin').count()
        regular_users = User.query.join(User.roles).filter(Role.name == 'user').count()
        
        # Performance statistics
        if total_attempts > 0:
            avg_score = db.session.query(func.avg(Score.total_scored)).scalar()
            avg_percentage = db.session.query(func.avg(
                func.cast(Score.total_scored, db.Float) / func.cast(Score.total_questions, db.Float) * 100
            )).scalar()
        else:
            avg_score = 0
            avg_percentage = 0
        
        # Top performing quizzes
        top_quizzes = db.session.query(
            Quiz.title,
            func.count(Score.id).label('attempts'),
            func.avg(func.cast(Score.total_scored, db.Float) / func.cast(Score.total_questions, db.Float) * 100).label('avg_percentage')
        ).join(Score).group_by(Quiz.id).order_by(desc('attempts')).limit(5).all()
        
        top_quizzes_data = []
        for quiz in top_quizzes:
            top_quizzes_data.append({
                'title': quiz.title,
                'attempts': quiz.attempts,
                'avg_percentage': round(quiz.avg_percentage, 2) if quiz.avg_percentage else 0
            })
        
        # Monthly activity (last 6 months)
        monthly_data = []
        for i in range(6):
            month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=1) + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            month_attempts = Score.query.filter(
                Score.time_stamp_of_attempt >= month_start,
                Score.time_stamp_of_attempt <= month_end
            ).count()
            
            monthly_data.append({
                'month': month_start.strftime('%B %Y'),
                'attempts': month_attempts
            })
        
        monthly_data.reverse()
        
        return {
            'dashboard_type': 'admin',
            'statistics': {
                'total_users': total_users,
                'total_subjects': total_subjects,
                'total_chapters': total_chapters,
                'total_quizzes': total_quizzes,
                'total_questions': total_questions,
                'total_attempts': total_attempts,
                'active_quizzes': active_quizzes,
                'inactive_quizzes': inactive_quizzes,
                'admin_users': admin_users,
                'regular_users': regular_users,
                'avg_score': round(avg_score, 2) if avg_score else 0,
                'avg_percentage': round(avg_percentage, 2) if avg_percentage else 0
            },
            'charts': {
                'top_quizzes': top_quizzes_data,
                'monthly_activity': monthly_data,
                'quiz_status': [
                    {'status': 'Active', 'count': active_quizzes},
                    {'status': 'Inactive', 'count': inactive_quizzes}
                ],
                'user_types': [
                    {'type': 'Admin', 'count': admin_users},
                    {'type': 'Regular Users', 'count': regular_users}
                ]
            },
            'recent_scores': recent_scores_data
        }, 200
    
    def _get_user_dashboard(self, user):
        """User dashboard with personal statistics"""
        # User's quiz attempts
        user_scores = Score.query.filter_by(user_id=user.id).all()
        total_attempts = len(user_scores)
        total_quizzes_available = Quiz.query.filter_by(is_active=True).count()
        
        # Performance statistics
        if user_scores:
            total_scored = sum(score.total_scored for score in user_scores)
            total_possible = sum(score.total_questions for score in user_scores)
            average_score = total_scored / len(user_scores)
            average_percentage = (total_scored / total_possible * 100) if total_possible > 0 else 0
            
            # Best score
            best_score = max(user_scores, key=lambda x: x.total_scored)
            
            # Recent performance (last 5 attempts)
            recent_scores = Score.query.filter_by(user_id=user.id).order_by(Score.time_stamp_of_attempt.desc()).limit(5).all()
            recent_performance = []
            for score in recent_scores:
                percentage = (score.total_scored / score.total_questions * 100) if score.total_questions > 0 else 0
                recent_performance.append({
                    'quiz_title': score.quiz.title,
                    'score': score.total_scored,
                    'total': score.total_questions,
                    'percentage': round(percentage, 2),
                    'date': score.time_stamp_of_attempt.strftime('%Y-%m-%d')
                })
        else:
            average_score = 0
            average_percentage = 0
            best_score = None
            recent_performance = []
        
        # Available quizzes by subject
        available_quizzes = db.session.query(
            Subject.name.label('subject_name'),
            func.count(Quiz.id).label('quiz_count')
        ).select_from(Subject).join(Chapter).join(Quiz).filter(Quiz.is_active == True).group_by(Subject.id).all()
        
        available_quizzes_data = []
        for quiz in available_quizzes:
            available_quizzes_data.append({
                'subject': quiz.subject_name,
                'quiz_count': quiz.quiz_count
            })
        
        # Monthly activity (last 6 months)
        monthly_data = []
        for i in range(6):
            month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=1) + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            month_attempts = Score.query.filter(
                Score.user_id == user.id,
                Score.time_stamp_of_attempt >= month_start,
                Score.time_stamp_of_attempt <= month_end
            ).count()
            
            monthly_data.append({
                'month': month_start.strftime('%B %Y'),
                'attempts': month_attempts
            })
        
        monthly_data.reverse()
        
        return {
            'dashboard_type': 'user',
            'statistics': {
                'total_attempts': total_attempts,
                'total_quizzes_available': total_quizzes_available,
                'average_score': round(average_score, 2),
                'average_percentage': round(average_percentage, 2),
                'best_score': best_score.convert_to_json() if best_score else None
            },
            'charts': {
                'recent_performance': recent_performance,
                'available_quizzes': available_quizzes_data,
                'monthly_activity': monthly_data
            },
            'user_info': {
                'full_name': user.full_name,
                'qualification': user.qualification,
                'member_since': user.created_at.strftime('%B %Y') if user.created_at else None
            }
        }, 200 