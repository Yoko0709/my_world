from flask import Blueprint, request, jsonify
from models import db, Mood, Profile

routes = Blueprint('routes', __name__)

@routes.route('/api/profile')
def get_profile():
    print("📡 /api/profile 被调用")
    profile = Profile.query.first()
    return jsonify({
        "display_name": profile.display_name,
        "welcome_message": profile.welcome_message,
        "today_phrase": profile.today_phrase,
        "tagline": profile.tagline,
        "avatar_url": profile.avatar_url,
        "background_url": profile.background_url,
        "current_status": profile.current_status,
    })


routes = Blueprint('routes', __name__)

# 获取所有 mood（最新在前）
@routes.route('/api/moods', methods=['GET'])
def get_moods():
    moods = Mood.query.order_by(Mood.timestamp.desc()).all()
    return jsonify([
        {
            "id": mood.id,
            "content": mood.content,
            "emoji": mood.emoji,
            "timestamp": mood.timestamp.isoformat(),
            "image_url": mood.image_url
        } for mood in moods
    ])

# 添加新 mood
@routes.route('/api/moods', methods=['POST'])
def add_mood():
    data = request.get_json()
    mood = Mood(
        content=data.get('content'),
        emoji=data.get('emoji'),
        image_url=data.get('image_url')
    )
    db.session.add(mood)
    db.session.commit()
    return jsonify({"message": "Mood created", "id": mood.id}), 201
