from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email

class RegistrationForm(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Sign In')
