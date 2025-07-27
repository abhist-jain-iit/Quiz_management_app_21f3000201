from .base import BaseModel, db

class Question(BaseModel):
    __tablename__ = 'questions'
    
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(500), nullable=False)
    option2 = db.Column(db.String(500), nullable=False)
    option3 = db.Column(db.String(500))
    option4 = db.Column(db.String(500))
    correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4
    marks = db.Column(db.Integer, default=1)
    
    def convert_to_json(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_statement': self.question_statement,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correct_option': self.correct_option,
            'marks': self.marks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Question {self.id}>'