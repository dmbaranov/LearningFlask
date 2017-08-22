from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    about_me = TextAreaField('About me', validators=[validators.DataRequired()])

    def __init__(self, original_username, *args, **kwargs):
        super().__init__()
        self.original_username = original_username

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.username.data == self.original_username:
            return True

        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("This username has been taken already!")
            return False

        return True
