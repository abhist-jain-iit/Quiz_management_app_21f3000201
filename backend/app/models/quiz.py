from .base import BaseModel, db
from datetime import datetime

class Quiz(BaseModel):
    __tablename__ = 'quizzes'
    
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    time_duration = db.Column(db.Time, nullable=False)  # HH:MM format
    remarks = db.Column(db.Text)
    title = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy='dynamic')
    
    def convert_to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'chapter_id': self.chapter_id,
            'chapter_name': self.chapter.name if self.chapter else None,
            'subject_name': self.chapter.subject.name if self.chapter and self.chapter.subject else None,
            'date_of_quiz': self.date_of_quiz.isoformat() if self.date_of_quiz else None,
            'time_duration': str(self.time_duration) if self.time_duration else None,
            'remarks': self.remarks,
            'is_active': self.is_active,
            'question_count': self.questions.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Quiz {self.title}>'
