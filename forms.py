from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TimeField, SubmitField, PasswordField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from datetime import date
from models import User

class PatientRegistrationForm(FlaskForm):
    pat_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    contact_num = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_dob(self, field):
        if field.data > date.today():
            raise ValidationError("Date of birth cannot be in the future.")

class PatientUpdateForm(FlaskForm):
    pat_name = StringField('Full Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    contact_num = StringField('Contact Number', validators=[DataRequired()])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class DoctorForm(FlaskForm):
    doc_name = StringField('Doctor Name', validators=[DataRequired(), Length(min=2, max=100, message="Name must be between 2 and 100 characters")])
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    
    contact_num = StringField('Contact Number', validators=[DataRequired(),Length(min=10, max=15, message="Phone number must be 10-15 digits"),Regexp(r'^\+?1?\d{9,15}$', message="Invalid phone format (digits only)")])
    
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    specialization = SelectField('Department', coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Save Doctor')

    def validate_dob(self, field):
        if field.data > date.today():
            raise ValidationError("Date of birth cannot be in the future.")


class PatientForm(FlaskForm):
    pat_name = StringField('Patient Name', validators=[DataRequired(), Length(min=2, max=100)])
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    contact_num = StringField('Contact Number', validators=[DataRequired(),Length(min=10, max=15),Regexp(r'^\d+$', message="Phone number must contain only digits")])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    
    submit = SubmitField('Save Patient')


class AppointmentForm(FlaskForm):
    doctor = SelectField('Select Doctor', coerce=int, validators=[DataRequired()])
    patient = SelectField('Select Patient', coerce=int, validators=[DataRequired()])
    date = DateField('Appointment Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time Slot', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')

    def validate_date(self, field):
        if field.data < date.today():
            raise ValidationError("Appointments cannot be booked in the past.")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TreatmentForm(FlaskForm):
    ailment = StringField('Ailment', validators=[DataRequired(), Length(max=100)])
    prescription = TextAreaField('Prescription', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Treatment')

class AvailabilityForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time_slot = SelectField('Time Slot', choices=[
        ('09:00', '09:00 - 11:00'),
        ('11:00', '11:00 - 13:00'),
        ('13:00', '13:00 - 15:00'),
        ('15:00', '15:00 - 17:00'),
        ('17:00', '17:00 - 19:00'),
        ('19:00', '19:00 - 21:00')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Availability')

    def validate_date(self, field):
        if field.data < date.today():
            raise ValidationError("You cannot set availability for past dates.")
        
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')