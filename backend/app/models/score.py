from .base import BaseModel, db
from datetime import datetime

class Score(BaseModel):
    __tablename__ = 'scores'
    
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Time)  # Actual time taken to complete
    
    # Unique constraint to prevent multiple attempts (if needed)
    # __table_args__ = (db.UniqueConstraint('quiz_id', 'user_id'),)
    
    def __repr__(self):
        return f'<Score User:{self.user_id} Quiz:{self.quiz_id} Score:{self.total_scored}>'