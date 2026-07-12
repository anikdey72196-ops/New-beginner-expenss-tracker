from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email

class RegistrationForm(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Register')

class LoginForm(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Sign In')
