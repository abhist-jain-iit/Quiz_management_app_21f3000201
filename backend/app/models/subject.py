from .base import BaseModel
from app.database import db

class Subject(BaseModel):
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    # Relationships
    chapters = db.relationship("Chapter", backref="subject", cascade="all, delete-orphan", lazy=True)

    def convert_to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'chapters_count': len(self.chapters) if self.chapters else 0
        }