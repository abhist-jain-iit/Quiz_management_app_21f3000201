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
    
    def __repr__(self):
        return f'<Chapter {self.name}>'