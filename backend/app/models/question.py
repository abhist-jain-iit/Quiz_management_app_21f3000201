import json
from .base import BaseModel
from app.database import db

class Question(BaseModel):
    question_statement = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    def get_options_list(self):
        # Return options as a list 
        return [self.option1, self.option2, self.option3, self.option4]

    def get_correct_answer(self):
        # Get the correct answer text 
        options = self.get_options_list()
        if 1 <= self.correct_option <= 4:
            return options[self.correct_option - 1]
        return None

    def is_correct_answer(self, selected_option):
        # Check if selected option is correct 
        return selected_option == self.correct_option

    def convert_to_json(self, include_correct=False):
        # Convert to JSON with option to include correct answer 
        data = {
            'id': self.id,
            'question_statement': self.question_statement,
            'options': self.get_options_list(),
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'quiz_id': self.quiz_id,
            'quiz_name': self.quiz.name if self.quiz else None,
        }
        
        # Only include correct answer if explicitly requested (for admin or results)
        if include_correct:
            data['correct_option'] = self.correct_option
            data['correct_answer'] = self.get_correct_answer()
            
        return data