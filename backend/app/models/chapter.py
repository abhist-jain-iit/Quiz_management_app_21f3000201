from .base import BaseModel
from app.database import db

class Chapter(BaseModel):
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    # Relationships
    quizzes = db.relationship("Quiz", backref="chapter", cascade="all, delete-orphan", lazy=True)

    def convert_to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'quizzes_count': len(self.quizzes) if self.quizzes else 0
        }