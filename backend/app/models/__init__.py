# Import all models.
from .base import BaseModel
from .user import User
from .subject import Subject
from .chapter import Chapter
from .quiz import Quiz
from .question import Question
from .score import Score

# Making all the models files available for import
__all__ = [
    'BaseModel',
    'User', 
    'Subject',
    'Chapter',
    'Quiz',
    'Question',
    'Score'
]