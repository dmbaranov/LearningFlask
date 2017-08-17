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
db = SQLAlchemy(app)

from app import views, models
