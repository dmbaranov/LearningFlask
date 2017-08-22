from flask import Blueprint

profile = Blueprint('profile', __name__, template_folder='templates')
ALLOWED_AVATAR_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


from app.profile import views