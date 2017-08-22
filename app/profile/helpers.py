from flask_login import current_user
from datetime import datetime
from app import db
from app.models import User
from app.profile import ALLOWED_AVATAR_EXTENSIONS


def update_last_seen():
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
        user.last_seen = datetime.now()
        db.session.commit()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS