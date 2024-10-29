from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=255)])
    two_factor_code = StringField('2FA Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Sign In')

class SignupForm(FlaskForm):
    name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    second_name = StringField('Second Name', validators=[Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    second_last_name = StringField('Second Last Name', validators=[Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=25)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('lawyer', 'Lawyer'), ('assistant', 'Assistant')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=255)])
    submit = SubmitField('Sign Up')
