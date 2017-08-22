import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.helpers import j2_dateformat

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))
app.jinja_env.filters['dateformat'] = j2_dateformat
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'auth.login_page'
lm.login_message = "Sign in to access this page"
lm.login_message_category = 'danger'
lm.refresh_view = 'auth.relogin'
lm.needs_refresh_message = "Please reauthenticate to access this page."
lm.needs_refresh_message_category = 'info'

from app import models
from app.main import main
from app.auth import auth
from app.post import post
from app.profile import profile
from app.profile.helpers import update_last_seen

app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(post, url_prefix='/post')
app.register_blueprint(profile, url_prefix='/profile')


from app.models import User


@lm.user_loader
def get_user(session_token):
    return User.query.filter_by(session_token=session_token).first()


@app.before_request
def before_request():
    update_last_seen()


@app.errorhandler(404)
def not_found_page(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error_page(error):
    db.session.rollback()
    return render_template('500.html'), 500


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/logs.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.setHandler(file_handler)
    app.logger.info('Application has been launched')