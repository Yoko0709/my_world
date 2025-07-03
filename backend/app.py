from flask import Flask
from flask_cors import CORS
from models import db, Profile
from routes import routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
CORS(app)
db.init_app(app)

app.register_blueprint(routes)

# 自动建表 + 初始化数据（首次运行）
with app.app_context():
    db.create_all()
    if not Profile.query.first():
        profile = Profile(
            display_name="Ren Zhiyan",
            welcome_message="你好，旅人。",
            today_phrase="风来无语，叶落有声。",
            tagline="世界不爆炸我不放假 ✨",
            avatar_url="/static/avatar.jpg",
            background_url="/static/bg.jpg",
            current_status="在东京大学研究AI与社会的交叉"
        )
        db.session.add(profile)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)

