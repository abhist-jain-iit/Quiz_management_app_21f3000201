from .base import BaseModel, db
from datetime import datetime

class Score(BaseModel):
    __tablename__ = 'scores'
    
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.String(5))  # Actual time taken to complete in HH:MM format
    
    # Unique constraint to prevent multiple attempts (if needed)
    # __table_args__ = (db.UniqueConstraint('quiz_id', 'user_id'),)
    
    def convert_to_json(self):
        # Calculate percentage based on actual total possible marks
        percentage = 0
        if self.quiz and self.total_questions > 0:
            from sqlalchemy import func
            from .question import Question
            total_possible_marks = db.session.query(func.sum(Question.marks)).filter_by(quiz_id=self.quiz_id).scalar() or 0
            if total_possible_marks > 0:
                percentage = round((self.total_scored / total_possible_marks * 100), 2)

        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz.title if self.quiz else None,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'time_stamp_of_attempt': self.time_stamp_of_attempt.isoformat() if self.time_stamp_of_attempt else None,
            'total_scored': self.total_scored,
            'total_questions': self.total_questions,
            'percentage': percentage,
            'time_taken': self.time_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Score User:{self.user_id} Quiz:{self.quiz_id} Score:{self.total_scored}>'