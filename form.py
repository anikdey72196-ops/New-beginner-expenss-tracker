from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email

class Registration(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    phonenumber=StringField('phonenumber',validators=[DataRequired()])
    email=EmailField('email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Sign Up')

class login(FlaskForm):
    email=EmailField('email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Sign In')
