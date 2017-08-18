import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.helpers import j2_dateformat

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))
app.jinja_env.filters['dateformat'] = j2_dateformat
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login_page'
lm.login_message = "Sign in to access this page"
lm.login_message_category = 'danger'
lm.refresh_view = 'relogin'
lm.needs_refresh_message = "Please reauthenticate to access this page."
lm.needs_refresh_message_category = 'info'

db = SQLAlchemy(app)

from app import views, models
