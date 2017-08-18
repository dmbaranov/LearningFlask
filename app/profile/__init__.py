from flask import Blueprint

profile = Blueprint('profile', __name__, template_folder='templates')

from app.profile import views