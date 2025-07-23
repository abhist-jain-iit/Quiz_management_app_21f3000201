from datetime import datetime, date, time
from .base import BaseModel
from app.database import db

class Quiz(BaseModel):
    name = db.Column(db.String(120), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.String(10), nullable=False)  # Format: HH:MM
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    remarks = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Relationships
    questions = db.relationship("Question", backref="quiz", cascade="all, delete-orphan", lazy=True)
    scores = db.relationship("Score", backref="quiz", cascade="all, delete-orphan", lazy=True)

    def get_start_datetime(self):
        # Get combined start datetime 
        return datetime.combine(self.start_date, self.start_time)

    def get_end_datetime(self):
        # Get combined end datetime 
        return datetime.combine(self.end_date, self.end_time)

    def is_active(self):
        # Check if quiz is currently active 
        now = datetime.now()
        return self.get_start_datetime() <= now <= self.get_end_datetime()

    def is_upcoming(self):
        # Check if quiz is upcoming 
        now = datetime.now()
        return now < self.get_start_datetime()

    def is_completed(self):
        # Check if quiz is completed 
        now = datetime.now()
        return now > self.get_end_datetime()

    def convert_to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'date_of_quiz': self.date_of_quiz.strftime('%Y-%m-%d') if self.date_of_quiz else None,
            'time_duration': self.time_duration,
            'duration': self.duration,
            'remarks': self.remarks,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'start_time': self.start_time.strftime('%H:%M:%S') if self.start_time else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'end_time': self.end_time.strftime('%H:%M:%S') if self.end_time else None,
            'chapter_id': self.chapter_id,
            'chapter_name': self.chapter.name if self.chapter else None,
            'subject_name': self.chapter.subject.name if self.chapter and self.chapter.subject else None,
            'questions_count': len(self.questions) if self.questions else 0,
            'is_active': self.is_active(),
            'is_upcoming': self.is_upcoming(),
            'is_completed': self.is_completed()
        }