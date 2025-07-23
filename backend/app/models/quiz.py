from .base import BaseModel, db
from datetime import datetime

class Quiz(BaseModel):
    __tablename__ = 'quizzes'
    
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    time_duration = db.Column(db.Time, nullable=False)  # HH:MM format
    remarks = db.Column(db.Text)
    title = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy='dynamic')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'
