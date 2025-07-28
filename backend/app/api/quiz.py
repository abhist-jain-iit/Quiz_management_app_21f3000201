from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models import db, User, Subject, Chapter, Quiz
from ..auth import admin_required

class QuizApi(Resource):
    def get(self, quiz_id=None):
        """Get all quizzes or specific quiz"""
        if quiz_id:
            quiz = Quiz.query.get(quiz_id)
            if quiz:
                quiz_data = quiz.convert_to_json()
                return quiz_data, 200
            return {'message': 'Quiz does not exist.'}, 404

        # For quiz lists, get query parameters
        search_query = request.args.get('search', '').strip()
        chapter_id = request.args.get('chapter_id', '')
        is_active = request.args.get('is_active', '')

        if search_query:
            quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{search_query}%"))
        else:
            quizzes = Quiz.query

        if chapter_id:
            quizzes = quizzes.filter_by(chapter_id=chapter_id)

        if is_active:
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
        cache = current_app.cache
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
        
        # Validate time duration format
        time_duration = data.get('time_duration').strip()
        try:
            time_parts = time_duration.split(':')
            if len(time_parts) != 2:
                return {'message': 'Invalid time format. Use HH:MM'}, 400
            hours, minutes = int(time_parts[0]), int(time_parts[1])
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                return {'message': 'Invalid time values'}, 400
            # Store as string in HH:MM format
            duration = f"{hours:02d}:{minutes:02d}"
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
        
        # Cache invalidation removed for simplicity

        return new_quiz.convert_to_json(), 201

    @jwt_required()
    @admin_required()
    def put(self, quiz_id):
        """Update quiz (Admin only)"""
        cache = current_app.cache
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
        
        # Validate time duration format
        time_duration = data.get('time_duration').strip()
        try:
            time_parts = time_duration.split(':')
            if len(time_parts) != 2:
                return {'message': 'Invalid time format. Use HH:MM'}, 400
            hours, minutes = int(time_parts[0]), int(time_parts[1])
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                return {'message': 'Invalid time values'}, 400
            # Store as string in HH:MM format
            duration = f"{hours:02d}:{minutes:02d}"
        except (ValueError, IndexError):
            return {'message': 'Invalid time format. Use HH:MM'}, 400
        
        quiz.title = data.get('title').strip()
        quiz.chapter_id = data.get('chapter_id')
        quiz.date_of_quiz = quiz_date
        quiz.time_duration = duration
        quiz.remarks = data.get('remarks', '').strip()
        quiz.is_active = data.get('is_active', quiz.is_active)
        
        db.session.commit()
        
        cache.delete('all_quizzes')
        return quiz.convert_to_json(), 200

    @jwt_required()
    @admin_required()
    def delete(self, quiz_id):
        """Delete quiz and all associated data (Admin only)"""
        cache = current_app.cache
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz does not exist.'}, 404

        try:
            # Count what will be deleted for confirmation message
            total_questions = len(quiz.questions)
            total_scores = len(quiz.scores)

            # Delete all questions for this quiz
            for question in quiz.questions:
                db.session.delete(question)

            # Delete all scores for this quiz
            for score in quiz.scores:
                db.session.delete(score)

            # Delete the quiz
            db.session.delete(quiz)
            db.session.commit()

            # Invalidate caches
            try:
                cache.clear()
            except Exception as e:
                print(f"Cache clear error: {e}")

            return {
                'message': f'Quiz "{quiz.title}" deleted successfully along with {total_questions} questions and {total_scores} quiz attempts.'
            }, 200

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting quiz: {e}")
            return {'message': 'Error occurred while deleting quiz.'}, 500

    def _invalidate_quiz_caches(self, cache):
        """Invalidate all quiz-related caches"""
        try:
            # Delete common quiz list cache patterns
            cache_patterns = [
                'all_quizzes',
                'quizzes_list__',  # Empty search, chapter, active
                'quizzes_list___true',  # Active quizzes
                'quizzes_list___false',  # Inactive quizzes
            ]

            for pattern in cache_patterns:
                try:
                    cache.delete(pattern)
                except:
                    pass  # Ignore cache deletion errors

            # Clear all cache to be safe (simple approach)
            try:
                cache.clear()
            except:
                pass  # Ignore if clear is not supported
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            # Continue execution even if cache fails