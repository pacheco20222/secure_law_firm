from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired

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



class CaseForm(FlaskForm):
    client_name = StringField('Client Name', validators=[DataRequired()])
    client_email = StringField('Client Email', validators=[DataRequired()])
    lawyer_id = SelectField('Assign to Lawyer', coerce=int, validators=[DataRequired()])
    assistant_id = SelectField('Assign to Assistant (Optional)', coerce=int)
    case_title = StringField('Case Title', validators=[DataRequired()])
    case_description = TextAreaField('Description')
    case_type = StringField('Case Type', validators=[DataRequired()])
    court_date = DateField('Court Date')
    judge_name = StringField('Judge Name')
    document_title = StringField('Document Title', validators=[DataRequired()])
    document_description = TextAreaField('Document Description')
    submit = SubmitField('Create Case')
