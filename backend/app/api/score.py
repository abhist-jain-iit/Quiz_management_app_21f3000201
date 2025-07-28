from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models import db, User, Quiz, Question, Score
from ..auth import user_required

class ScoreApi(Resource):
    @jwt_required()
    def get(self, score_id=None):
        """Get all scores or specific score"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if score_id:
            score = Score.query.get(score_id)
            if score:
                # Users can only see their own scores, admins can see all
                if not user.is_admin() and score.user_id != current_user_id:
                    return {'message': 'Access denied'}, 403
                return score.convert_to_json(), 200
            return {'message': 'Score does not exist.'}, 404

        # Filter scores based on user role
        if user.is_admin():
            scores = Score.query
        else:
            scores = Score.query.filter_by(user_id=current_user_id)
        
        quiz_id = request.args.get('quiz_id')
        if quiz_id:
            scores = scores.filter_by(quiz_id=quiz_id)
        
        scores = scores.order_by(Score.time_stamp_of_attempt.desc()).all()
        
        score_list = []
        for score in scores:
            score_list.append(score.convert_to_json())
        return score_list, 200

    @jwt_required()
    @user_required()
    def post(self):
        """Submit quiz attempt and calculate score"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not (data.get('quiz_id') and data.get('answers') and data.get('time_taken')):
            return {'message': 'Bad request! quiz_id, answers, and time_taken are required.'}, 400
        
        # Check if quiz exists and is active
        quiz = Quiz.query.get(data.get('quiz_id'))
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        
        if not quiz.is_active:
            return {'message': 'Quiz is not active'}, 400
        
        # Check if user has exceeded maximum attempts (5 attempts allowed)
        existing_attempts = Score.query.filter_by(
            quiz_id=data.get('quiz_id'),
            user_id=current_user_id
        ).count()

        if existing_attempts >= 5:
            return {'message': 'You have reached the maximum number of attempts (5) for this quiz'}, 409
        
        # Get all questions for this quiz
        questions = quiz.questions.all()
        if not questions:
            return {'message': 'No questions found for this quiz'}, 400
        
        # Calculate score
        total_questions = len(questions)
        total_scored = 0
        answers = data.get('answers', {})
        
        for question in questions:
            user_answer = answers.get(str(question.id))
            # Validate that user_answer is a valid option (1-4)
            if user_answer is not None and user_answer not in [1, 2, 3, 4]:
                return {'message': f'Invalid answer option {user_answer} for question {question.id}. Must be 1, 2, 3, or 4.'}, 400
            if user_answer and user_answer == question.correct_option:
                total_scored += question.marks
        
        # Validate time taken format
        time_taken = data.get('time_taken').strip()
        try:
            time_parts = time_taken.split(':')
            if len(time_parts) != 2:
                return {'message': 'Invalid time format. Use HH:MM'}, 400
            hours, minutes = int(time_parts[0]), int(time_parts[1])
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                return {'message': 'Invalid time values'}, 400
            # Store as string in HH:MM format
            time_taken = f"{hours:02d}:{minutes:02d}"
        except (ValueError, IndexError):
            return {'message': 'Invalid time format. Use HH:MM'}, 400
        
        # Create score record
        new_score = Score(
            quiz_id=data.get('quiz_id'),
            user_id=current_user_id,
            total_scored=total_scored,
            total_questions=total_questions,
            time_taken=time_taken
        )
        
        db.session.add(new_score)
        db.session.commit()
        
        return new_score.convert_to_json(), 201

class QuizAttemptApi(Resource):
    @jwt_required()
    @user_required()
    def get(self, quiz_id):
        """Get quiz for attempt (without correct answers)"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        
        if not quiz.is_active:
            return {'message': 'Quiz is not active'}, 400
        
        # Get questions without correct answers
        questions = quiz.questions.all()
        questions_data = []
        
        for question in questions:
            questions_data.append({
                'id': question.id,
                'question_statement': question.question_statement,
                'option1': question.option1,
                'option2': question.option2,
                'option3': question.option3,
                'option4': question.option4,
                'marks': question.marks
            })
        
        return {
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'time_duration': str(quiz.time_duration),
                'remarks': quiz.remarks,
                'question_count': len(questions_data)
            },
            'questions': questions_data
        }, 200

class DashboardApi(Resource):
    @jwt_required()
    def get(self):
        """Get dashboard statistics"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.is_admin():
            # Admin dashboard
            total_users = User.query.filter_by(is_active=True).count()
            total_subjects = db.session.query(db.func.count(db.distinct(Quiz.chapter_id))).scalar()
            total_quizzes = Quiz.query.count()
            total_attempts = Score.query.count()
            
            # Recent scores
            recent_scores = Score.query.order_by(Score.time_stamp_of_attempt.desc()).limit(10).all()
            recent_scores_data = [score.convert_to_json() for score in recent_scores]
            
            return {
                'dashboard_type': 'admin',
                'statistics': {
                    'total_users': total_users,
                    'total_subjects': total_subjects,
                    'total_quizzes': total_quizzes,
                    'total_attempts': total_attempts
                },
                'recent_scores': recent_scores_data
            }, 200
        else:
            # User dashboard
            user_scores = Score.query.filter_by(user_id=current_user_id).all()
            total_attempts = len(user_scores)
            total_quizzes_available = Quiz.query.filter_by(is_active=True).count()
            
            if user_scores:
                average_score = sum(score.total_scored for score in user_scores) / len(user_scores)
                best_score = max(user_scores, key=lambda x: x.total_scored)
            else:
                average_score = 0
                best_score = None
            
            # Recent attempts
            recent_scores = Score.query.filter_by(user_id=current_user_id).order_by(Score.time_stamp_of_attempt.desc()).limit(5).all()
            recent_scores_data = [score.convert_to_json() for score in recent_scores]
            
            return {
                'dashboard_type': 'user',
                'statistics': {
                    'total_attempts': total_attempts,
                    'total_quizzes_available': total_quizzes_available,
                    'average_score': round(average_score, 2),
                    'best_score': best_score.convert_to_json() if best_score else None
                },
                'recent_scores': recent_scores_data
            }, 200 