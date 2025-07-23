import json
from datetime import datetime
from .base import BaseModel
from app.database import db

class Score(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.Column(db.Text, nullable=False)  # JSON format: {question_id: selected_option}

    def add_answers(self, answers_dict):
        # Store user answers as JSON 
        self.answers = json.dumps(answers_dict)

    def get_answers(self):
        # Retrieve user answers from JSON 
        try:
            return json.loads(self.answers)
        except (json.JSONDecodeError, TypeError):
            return {}

    def calculate_score(self, questions):
        # Calculate score based on questions and user answers.
        user_answers = self.get_answers()
        correct_count = 0
        
        for question in questions:
            user_answer = user_answers.get(str(question.id))
            if user_answer and question.is_correct_answer(int(user_answer)):
                correct_count += 1
        
        self.total_questions = len(questions)
        self.correct_answers = correct_count
        self.total_scored = correct_count
        self.percentage = (correct_count / len(questions)) * 100 if questions else 0

    def get_time_taken(self):
        # Get time taken to complete quiz in minutes 
        if self.start_time and self.end_time:
            time_diff = self.end_time - self.start_time
            return round(time_diff.total_seconds() / 60, 2)
        return 0

    def convert_to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'quiz_id': self.quiz_id,
            'quiz_name': self.quiz.name if self.quiz else None,
            'chapter_name': self.quiz.chapter.name if self.quiz and self.quiz.chapter else None,
            'subject_name': self.quiz.chapter.subject.name if self.quiz and self.quiz.chapter and self.quiz.chapter.subject else None,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'total_scored': self.total_scored,
            'percentage': round(self.percentage, 2),
            'time_stamp_of_attempt': self.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M:%S') if self.time_stamp_of_attempt else None,
            'time_taken_minutes': self.get_time_taken(),
            'answers': self.get_answers()
        }