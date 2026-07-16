from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email,Length

class RegistrationForm(FlaskForm):
    username=StringField('username',validators=[
        DataRequired(),
        Length(min=3, max=80, message="Username must be between 3 and 80 characters.")
    ])
    password=PasswordField('password',validators=[
        DataRequired(),
        Length(min=8, max=128, message="Password must be between 8 and 128 characters.")
    ])
    submit=SubmitField('Register')

class LoginForm(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Sign In')
