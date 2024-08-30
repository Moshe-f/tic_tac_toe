# Web Forms for tic tac toe.

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


# Class for User Form
class UserForm(FlaskForm):
    """User Form.

    Args:
        FlaskForm (form): subclass of WTForms.
    """
    username: str = StringField("Username", validators=[DataRequired()])
    about_player: str = StringField("About Player")
    old_password: str = PasswordField("Old Password", validators=[DataRequired()])
    password_hash: str = PasswordField("Password", validators=[DataRequired()])
    password_hash2: str = PasswordField(
        "Confirm Password", validators=[DataRequired()])
    submit: str = SubmitField("Submit")


# login Class for Form
class LoginForm(FlaskForm):
    """Login form.

    Args:
        FlaskForm (form): subclass of WTForms.
    """
    username: str = StringField("username", validators=[DataRequired()])
    password: str = PasswordField("Password", validators=[DataRequired()])
    submit: str = SubmitField("Submit")
