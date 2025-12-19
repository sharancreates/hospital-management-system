from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) 

    patient = db.relationship('Patient', back_populates='user', uselist=False)
    doctor = db.relationship('Doctor', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)
    
class Doctor(db.Model):
    doctor_id = db.Column(db.Integer, primary_key = True)
    doc_name = db.Column(db.String(100), nullable = False)
    gender = db.Column(db.String(100), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    contact_num = db.Column(db.String(15), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    specialization = db.Column(db.String(80), db.ForeignKey('department.department_id'))

   # appointments = db.relationship('Appointment', backref = 'doctor', lazy = True)
    user = db.relationship('User', back_populates='doctor')
    appointments = db.relationship('Appointment', back_populates='doctor', lazy=True)
    department = db.relationship('Department', back_populates='doctors')

class Patient(db.Model):
    patient_id = db.Column(db.Integer, primary_key = True)
    pat_name = db.Column(db.String(100), nullable = False)
    gender = db.Column(db.String(100), nullable = False)
    contact_num = db.Column(db.String(15), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    age = db.Column(db.Integer, nullable = False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    # appointments = db.relationship('Appointment', backref = 'patient', lazy = True)
    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient', lazy=True)


class Appointment(db.Model):
    appointment_id = db.Column(db.Integer, primary_key = True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable = False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable = False)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    status = db.Column(db.String(80), nullable = False)

    doctor = db.relationship('Doctor', back_populates='appointments')
    patient = db.relationship('Patient', back_populates='appointments')
    treatment = db.relationship('Treatment', back_populates='appointment', uselist=False)
    # treatment = db.relationship('Treatment', backref = 'appointment', uselist = False)

class Treatment(db.Model):
    treatment_id = db.Column(db.Integer, primary_key = True)
    ailment = db.Column(db.Text, nullable = False)
    prescription = db.Column(db.Text, nullable = False)
    notes = db.Column(db.Text, nullable = False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'))

    appointment = db.relationship('Appointment', back_populates='treatment')

class Department(db.Model):
    department_id = db.Column(db.Integer, primary_key = True)
    department_name = db.Column(db.String(80), nullable = False)
    description = db.Column(db.Text, nullable = False)

    doctors = db.relationship('Doctor', back_populates='department', lazy=True)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'))
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)