from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired
from datetime import datetime, date

MAX_APPOINTMENTS_PER_SLOT = 10

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patient = db.relationship('Patient', back_populates='user', uselist=False, cascade="all, delete-orphan")
    doctor = db.relationship('Doctor', back_populates='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)
    
    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.user_id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=expires_sec)['user_id']
        except (BadSignature, SignatureExpired) as e:
            current_app.logger.warning(f"Invalid or expired password reset token signature: {str(e)}")
            return None
        return User.query.get(user_id)
    
class Doctor(db.Model):
    doctor_id = db.Column(db.Integer, primary_key = True)
    doc_name = db.Column(db.String(100), nullable = False)
    gender = db.Column(db.String(10), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    contact_num = db.Column(db.String(15), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='doctor')
    appointments = db.relationship('Appointment', back_populates='doctor', lazy=True)
    department = db.relationship('Department', back_populates='doctors')

class Patient(db.Model):
    patient_id = db.Column(db.Integer, primary_key = True)
    pat_name = db.Column(db.String(100), nullable = False)
    gender = db.Column(db.String(10), nullable = False)
    contact_num = db.Column(db.String(15), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient', lazy=True)

    @property
    def age(self):
        if not self.dob:
            return 0
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

class Appointment(db.Model):
    appointment_id = db.Column(db.Integer, primary_key = True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable = False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable = False, index=True)
    date = db.Column(db.Date, index=True)
    time = db.Column(db.Time)
    token_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(80), nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    doctor = db.relationship('Doctor', back_populates='appointments')
    patient = db.relationship('Patient', back_populates='appointments')
    treatment = db.relationship('Treatment', back_populates='appointment', uselist=False, cascade="all, delete-orphan")

class Treatment(db.Model):
    treatment_id = db.Column(db.Integer, primary_key = True)
    ailment = db.Column(db.Text, nullable = False)
    prescription = db.Column(db.Text, nullable = False)
    notes = db.Column(db.Text, nullable = False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'))
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    appointment = db.relationship('Appointment', back_populates='treatment')

class Department(db.Model):
    department_id = db.Column(db.Integer, primary_key = True)
    department_name = db.Column(db.String(80), nullable = False)
    description = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    doctors = db.relationship('Doctor', back_populates='department', lazy=True)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint('doctor_id', 'date', 'start_time', name='uq_doctor_availability'),)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(100), nullable=False)
    target_id = db.Column(db.Integer, nullable=True)
    changes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

class Ward(db.Model):
    ward_id = db.Column(db.Integer, primary_key=True)
    ward_name = db.Column(db.String(80), nullable=False)
    ward_type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    beds = db.relationship('Bed', back_populates='ward', lazy=True, cascade="all, delete-orphan")

class Bed(db.Model):
    bed_id = db.Column(db.Integer, primary_key=True)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.ward_id'), nullable=False)
    bed_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Available', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    ward = db.relationship('Ward', back_populates='beds')
    admissions = db.relationship('InpatientAdmission', back_populates='bed', lazy=True)

class InpatientAdmission(db.Model):
    admission_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    bed_id = db.Column(db.Integer, db.ForeignKey('bed.bed_id'), nullable=False)
    admitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    discharged_at = db.Column(db.DateTime, nullable=True)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    bed = db.relationship('Bed', back_populates='admissions')
    patient = db.relationship('Patient')
    nursing_notes = db.relationship('NursingNote', back_populates='admission', lazy=True, cascade="all, delete-orphan")
    bills = db.relationship('Bill', back_populates='admission', lazy=True)

class Nurse(db.Model):
    nurse_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_num = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User')
    nursing_notes = db.relationship('NursingNote', back_populates='nurse', lazy=True)

class NursingNote(db.Model):
    note_id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey('inpatient_admission.admission_id'), nullable=False)
    nurse_id = db.Column(db.Integer, db.ForeignKey('nurse.nurse_id'), nullable=False)
    note_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    admission = db.relationship('InpatientAdmission', back_populates='nursing_notes')
    nurse = db.relationship('Nurse', back_populates='nursing_notes')

class LabOrder(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Ordered', nullable=False)
    result_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patient = db.relationship('Patient')
    doctor = db.relationship('Doctor')

class InsurancePolicy(db.Model):
    policy_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    provider_name = db.Column(db.String(100), nullable=False)
    policy_number = db.Column(db.String(50), nullable=False)
    coverage_limit = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patient = db.relationship('Patient')

class Bill(db.Model):
    bill_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'), nullable=True)
    admission_id = db.Column(db.Integer, db.ForeignKey('inpatient_admission.admission_id'), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    insurance_covered = db.Column(db.Float, default=0.0, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(20), default='Unpaid', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patient = db.relationship('Patient')
    appointment = db.relationship('Appointment')
    admission = db.relationship('InpatientAdmission', back_populates='bills')

class Referral(db.Model):
    referral_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    referring_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    target_hospital = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patient = db.relationship('Patient')
    referring_doctor = db.relationship('Doctor')

class DrugInventory(db.Model):
    drug_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    dosage_form = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)