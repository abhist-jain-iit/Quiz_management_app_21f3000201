from app.database import db
from datetime import datetime

class BaseModel(db.Model):
    __abstract__ = True # Helps in ignoring this file.
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)