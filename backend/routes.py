from flask import Blueprint, jsonify
from models import Profile

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
