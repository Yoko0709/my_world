from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(50))
    welcome_message = db.Column(db.String(200))
    today_phrase = db.Column(db.String(100))
    tagline = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    background_url = db.Column(db.String(200))
    current_status = db.Column(db.String(100))

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    emoji = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(200))

