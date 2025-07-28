from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Quiz, Question
from ..auth import admin_required

class QuestionApi(Resource):
    def get(self, question_id=None):
        """Get all questions or specific question"""
        if question_id:
            question = Question.query.get(question_id)
            if question:
                return question.convert_to_json(), 200
            return {'message': 'Question does not exist.'}, 404

        search_query = request.args.get('search', '').strip()
        quiz_id = request.args.get('quiz_id')

        if search_query:
            questions = Question.query.filter(Question.question_statement.ilike(f"%{search_query}%"))
        else:
            questions = Question.query
        
        if quiz_id:
            questions = questions.filter_by(quiz_id=quiz_id)
        
        questions = questions.all()
        
        question_list = []
        for question in questions:
            question_list.append(question.convert_to_json())
        return question_list, 200

    @jwt_required()
    @admin_required()
    def post(self):
        """Create new question (Admin only)"""
        data = request.get_json()
        
        required_fields = ['question_statement', 'option1', 'option2', 'correct_option', 'quiz_id']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'Bad request! {field} is required.'}, 400
        
        if len(data.get('question_statement').strip()) < 3 or len(data.get('question_statement').strip()) > 1000:
            return {'message': 'Length of question should be between 3 and 1000 characters'}, 400
        
        # Check if quiz exists
        quiz = Quiz.query.get(data.get('quiz_id'))
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        
        # Validate correct option
        correct_option = data.get('correct_option')
        if correct_option not in [1, 2, 3, 4]:
            return {'message': 'Correct option must be 1, 2, 3, or 4'}, 400

        # Count available options
        available_options = 2  # option1 and option2 are required
        if data.get('option3'):
            available_options += 1
        if data.get('option4'):
            available_options += 1

        if correct_option > available_options:
            return {'message': f'Correct option {correct_option} is not available. Only {available_options} options provided.'}, 400
        
        # Check if question already exists in this quiz
        existing_question = Question.query.filter_by(
            question_statement=data.get('question_statement').strip(),
            quiz_id=data.get('quiz_id')
        ).first()
        
        if existing_question:
            return {"message": "Question already exists in this quiz."}, 409
        
        try:
            new_question = Question(
                question_statement=data.get('question_statement').strip(),
                option1=data.get('option1').strip(),
                option2=data.get('option2').strip(),
                option3=data.get('option3', '').strip() if data.get('option3') else None,
                option4=data.get('option4', '').strip() if data.get('option4') else None,
                correct_option=correct_option,
                quiz_id=data.get('quiz_id'),
                marks=data.get('marks', 1)
            )

            db.session.add(new_question)
            db.session.commit()

            return new_question.convert_to_json(), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error creating question: {e}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error creating question: {str(e)}'}, 500

    @jwt_required()
    @admin_required()
    def put(self, question_id):
        """Update question (Admin only)"""
        data = request.get_json()
        
        required_fields = ['question_statement', 'option1', 'option2', 'option3', 'option4', 'correct_option', 'quiz_id']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'Bad request! {field} is required.'}, 400
        
        if len(data.get('question_statement').strip()) < 3 or len(data.get('question_statement').strip()) > 1000:
            return {'message': 'Length of question should be between 3 and 1000 characters'}, 400
        
        # Check if quiz exists
        quiz = Quiz.query.get(data.get('quiz_id'))
        if not quiz:
            return {'message': 'Quiz not found'}, 400
        
        # Validate correct option
        correct_option = data.get('correct_option')
        if correct_option not in [1, 2, 3, 4]:
            return {'message': 'Correct option must be 1, 2, 3, or 4'}, 400
        
        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question does not exist.'}, 404
        
        # Check if question already exists in this quiz (excluding current question)
        existing_question = Question.query.filter_by(
            question_statement=data.get('question_statement').strip(),
            quiz_id=data.get('quiz_id')
        ).first()
        
        if existing_question and existing_question.id != question_id:
            return {"message": "Question already exists in this quiz."}, 409
        
        try:
            question.question_statement = data.get('question_statement').strip()
            question.option1 = data.get('option1').strip()
            question.option2 = data.get('option2').strip()
            question.option3 = data.get('option3').strip()
            question.option4 = data.get('option4').strip()
            question.correct_option = correct_option
            question.quiz_id = data.get('quiz_id')
            question.marks = data.get('marks', question.marks)

            db.session.commit()

            return question.convert_to_json(), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error updating question: {e}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error updating question: {str(e)}'}, 500

    @jwt_required()
    @admin_required()
    def delete(self, question_id):
        """Delete question (Admin only)"""
        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question does not exist.'}, 404
        
        db.session.delete(question)
        db.session.commit()
        
        return {'message': 'Question deleted successfully.'}, 200 