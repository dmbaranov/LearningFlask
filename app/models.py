from flask.ext.login import UserMixin
from datetime import datetime
from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(120))
    register_date = db.Column(db.DateTime, default=datetime.utcnow())
    posts_ids = db.relationship('Post', backref='author')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f'User <{self.id}>'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), index=True)
    content = db.Column(db.String)
    create_date = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author
        # self.author_id = author_id

    def __repr__(self):
        return f'Post <{self.id}>'
