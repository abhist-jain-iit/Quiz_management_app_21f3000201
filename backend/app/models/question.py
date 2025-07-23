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
    
    def __repr__(self):
        return f'<Question {self.id}>'