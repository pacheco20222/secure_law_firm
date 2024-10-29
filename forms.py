from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    two_factor_code = StringField('2FA Code', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class CreateUserForm(FlaskForm):
    name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    second_name = StringField('Second Name', validators=[Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    second_last_name = StringField('Second Last Name', validators=[Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    role = SelectField('Role', choices=[('lawyer', 'Lawyer'), ('legal_assistant', 'Legal Assistant')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=255)])
    submit = SubmitField('Create User')