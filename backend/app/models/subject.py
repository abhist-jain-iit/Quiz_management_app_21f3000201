from .base import BaseModel, db

class Subject(BaseModel):
    __tablename__ = 'subjects'
    
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    chapters = db.relationship('Chapter', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    
    def convert_to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Subject {self.name}>'