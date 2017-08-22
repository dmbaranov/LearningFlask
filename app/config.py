import os
from app import app


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static')
    POSTS_PER_PAGE = 3


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEVELOPMENT = True
