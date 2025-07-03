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
