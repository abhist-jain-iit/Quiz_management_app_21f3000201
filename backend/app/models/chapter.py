from .base import BaseModel, db

class Chapter(BaseModel):
    __tablename__ = 'chapters'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')

    # we have two things backref and back_populates.
    # backref uses one way and back_populates uses two way.
    
    # Unique constraint for chapter name within a subject
    __table_args__ = (db.UniqueConstraint('name', 'subject_id'),)
    
    def convert_to_json(self):
        from . import Quiz  # Import here to avoid circular imports
        quiz_count = db.session.query(Quiz).filter_by(chapter_id=self.id).count()
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'quiz_count': quiz_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Chapter {self.name}>'