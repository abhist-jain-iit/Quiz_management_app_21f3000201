from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Score, Quiz, Chapter, Subject, Question, db
from app.auth import admin_required
from sqlalchemy import func
import csv
import io
from datetime import datetime

export_bp = Blueprint('export', __name__)

@export_bp.route('/api/export/user-csv', methods=['POST'])
@jwt_required()
def export_user_csv_endpoint():
    """Export user's quiz data as CSV"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Get user's scores with quiz details
        scores = Score.query.filter_by(user_id=user_id).all()

        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Quiz Title',
            'Subject',
            'Chapter',
            'Date Taken',
            'Score',
            'Total Questions',
            'Percentage',
            'Quiz Date',
            'Duration',
            'Remarks'
        ])

        # Write data
        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            if quiz:
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id) if chapter else None

                # Calculate percentage based on actual total possible marks
                from sqlalchemy import func
                total_possible_marks = db.session.query(func.sum(Question.marks)).filter_by(quiz_id=quiz.id).scalar() or 0
                percentage = (score.total_scored / total_possible_marks * 100) if total_possible_marks > 0 else 0

                writer.writerow([
                    quiz.title,
                    subject.name if subject else 'Unknown',
                    chapter.name if chapter else 'Unknown',
                    score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M:%S'),
                    score.total_scored,
                    score.total_questions,
                    f"{percentage:.1f}%",
                    quiz.date_of_quiz.strftime('%Y-%m-%d') if quiz.date_of_quiz else '',
                    quiz.time_duration,
                    quiz.remarks or ''
                ])

        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=quiz_data_{user.username}_{datetime.now().strftime("%Y%m%d")}.csv'

        return response

    except Exception as e:
        print(f"Error exporting user CSV: {e}")
        return jsonify({'message': 'Export failed. Please try again.'}), 500

@export_bp.route('/api/export/admin-csv', methods=['POST'])
@jwt_required()
@admin_required()
def export_admin_csv_endpoint():
    """Export all users' quiz data as CSV (Admin only)"""
    try:
        # Get all users and their scores
        users = User.query.all()

        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'User ID',
            'Username',
            'Full Name',
            'Email',
            'Total Quizzes Taken',
            'Average Score',
            'Best Score',
            'Last Quiz Date',
            'Registration Date'
        ])

        # Write data
        for user in users:
            scores = Score.query.filter_by(user_id=user.id).all()

            if scores:
                total_quizzes = len(scores)
                total_percentage = 0
                valid_scores = 0

                # Calculate average percentage correctly
                for score in scores:
                    quiz = Quiz.query.get(score.quiz_id)
                    if quiz:
                        total_possible_marks = db.session.query(func.sum(Question.marks)).filter_by(quiz_id=quiz.id).scalar() or 0
                        if total_possible_marks > 0:
                            percentage = (score.total_scored / total_possible_marks * 100)
                            total_percentage += percentage
                            valid_scores += 1

                avg_score = total_percentage / valid_scores if valid_scores > 0 else 0

                # Find best score
                best_percentage = 0
                for score in scores:
                    quiz = Quiz.query.get(score.quiz_id)
                    if quiz:
                        total_possible_marks = db.session.query(func.sum(Question.marks)).filter_by(quiz_id=quiz.id).scalar() or 0
                        if total_possible_marks > 0:
                            percentage = (score.total_scored / total_possible_marks * 100)
                            if percentage > best_percentage:
                                best_percentage = percentage

                # Find last quiz date
                last_quiz = max(scores, key=lambda s: s.time_stamp_of_attempt)
                last_quiz_date = last_quiz.time_stamp_of_attempt.strftime('%Y-%m-%d')
            else:
                total_quizzes = 0
                avg_score = 0
                best_percentage = 0
                last_quiz_date = 'Never'

            writer.writerow([
                user.id,
                user.username,
                user.full_name,
                user.email,
                total_quizzes,
                f"{avg_score:.1f}%",
                f"{best_percentage:.1f}%",
                last_quiz_date,
                user.created_at.strftime('%Y-%m-%d') if user.created_at else ''
            ])

        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=admin_all_users_{datetime.now().strftime("%Y%m%d")}.csv'

        return response

    except Exception as e:
        print(f"Error exporting admin CSV: {e}")
        return jsonify({'message': 'Export failed. Please try again.'}), 500