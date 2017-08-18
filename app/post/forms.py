from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators


class PostForm(FlaskForm):
    title = StringField('Title', validators=[validators.DataRequired()])
    content = TextAreaField('Content', validators=[validators.DataRequired()])