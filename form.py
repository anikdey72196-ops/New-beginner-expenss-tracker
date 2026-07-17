from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email,Length

class RegistrationForm(FlaskForm):
    username=StringField('username',validators=[DataRequired(), Length(max=80)])
    password=PasswordField('password',validators=[DataRequired(), Length(max=72)])
    submit=SubmitField('Register')

class LoginForm(FlaskForm):
    username=StringField('username',validators=[DataRequired(), Length(max=80)])
    password=PasswordField('password',validators=[DataRequired(), Length(max=72)])
    submit=SubmitField('Sign In')
