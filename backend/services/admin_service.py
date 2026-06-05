from models import Doctor, Patient, User, Appointment, Availability, Department, MAX_APPOINTMENTS_PER_SLOT
from extensions import db, mail
from datetime import datetime, date
from werkzeug.security import generate_password_hash
from flask import current_app
from flask_mail import Message
from services.audit_service import log_audit
import string
import secrets
import os

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def send_welcome_email(email, password, role):
    msg = Message('Welcome to Arogya Hospital',
                  sender=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@arogya.in'),
                  recipients=[email])
    msg.body = f'''Hello,
 
Your {role} account has been created on the Arogya Hospital Management System.

Please use the following credentials to log in:
Email: {email}
Password: {password}

For security, we recommend that you change your password upon logging in.
'''
    
    if current_app.config.get('TESTING'):
        # In unit tests, run synchronously to support mock patching and avoid race conditions
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.warning(f"Error sending welcome email in test: {str(e)}")
        return

    # In development/production, run asynchronously in a background thread to prevent blocking the UI
    from threading import Thread
    app = current_app._get_current_object()

    def async_send():
        with app.app_context():
            try:
                mail.send(msg)
            except Exception as e:
                app.logger.warning(f"Error sending welcome email: {str(e)}")
                try:
                    log_dir = os.path.join(app.root_path, 'instance')
                    os.makedirs(log_dir, exist_ok=True)
                    log_path = os.path.join(log_dir, 'sent_emails.txt')
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(f"--- EMAIL SENT AT {datetime.now()} ---\n")
                        f.write(f"To: {email}\n")
                        f.write(f"Subject: Welcome to Arogya Hospital\n")
                        f.write(f"Body:\n{msg.body}\n")
                        f.write("-" * 40 + "\n\n")
                    app.logger.info(f"[SMTP Fallback] Welcome email written to {log_path}")
                except Exception as log_err:
                    app.logger.error(f"Failed to write welcome fallback: {str(log_err)}")

    Thread(target=async_send).start()

def create_doctor(data):
    doc_name = data.get('doc_name')
    base_email = f"{doc_name.lower().replace(' ', '.')}@arogya.in"
    email = base_email
    count = 1
    while User.query.filter_by(email=email).first():
        email = f"{base_email.split('@')[0]}.{count}@arogya.in"
        count += 1

    default_password = generate_password()
    hashed_pw = generate_password_hash(default_password)
    user = User(email=email, password_hash=hashed_pw, role='doctor')
    
    db.session.add(user)
    db.session.flush() 

    dob_str = data.get('dob')
    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

    doctor = Doctor(
        doc_name=doc_name,
        gender=data.get('gender'),
        dob=dob_date,
        contact_num=data.get('contact_num'),
        department_id=data.get('specialization'), 
        user_id=user.user_id
    )
    
    db.session.add(doctor)
    db.session.flush()
    log_audit("CREATE_DOCTOR", "Doctor", doctor.doctor_id, {"email": email})
    send_welcome_email(email, default_password, 'Doctor')
    db.session.commit()
    return doctor, email

def update_doctor(doctor_id, data):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.doc_name = data.get('doc_name', doctor.doc_name)
    doctor.gender = data.get('gender', doctor.gender)
    doctor.contact_num = data.get('contact_num', doctor.contact_num)
    doctor.department_id = data.get('specialization', doctor.department_id)
    
    dob_str = data.get('dob')
    if dob_str:
        doctor.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
    db.session.flush()
    log_audit("UPDATE_DOCTOR", "Doctor", doctor.doctor_id)
    db.session.commit()
    return doctor

def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.user_id:
        user = User.query.get(doctor.user_id)
        doctor.user_id = None
        db.session.flush()
        if user:
            db.session.delete(user)
        
    future_appts = Appointment.query.filter(
        Appointment.doctor_id == doctor_id, 
        Appointment.date >= date.today(), 
        Appointment.status != 'Cancelled'
    ).all()
    for appt in future_appts:
        appt.status = 'Cancelled'
        if appt.treatment:
            db.session.delete(appt.treatment)
        
    log_audit("DELETE_DOCTOR", "Doctor", doctor_id)
    db.session.commit()

def create_patient(data):
    pat_name = data.get('pat_name')
    email = data.get('email')
    
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already exists")

    default_password = generate_password()
    hashed_pw = generate_password_hash(default_password)
    user = User(email=email, password_hash=hashed_pw, role='patient')
    
    db.session.add(user)
    db.session.flush() 

    dob_str = data.get('dob')
    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

    # Patient has no age database column anymore (computed dynamically via dob)
    patient = Patient(
        pat_name=pat_name,
        gender=data.get('gender'),
        dob=dob_date,
        contact_num=data.get('contact_num'),
        user_id=user.user_id
    )
    
    db.session.add(patient)
    db.session.flush()
    log_audit("CREATE_PATIENT", "Patient", patient.patient_id, {"email": email})
    send_welcome_email(email, default_password, 'Patient')
    db.session.commit()
    return patient

def update_patient(patient_id, data):
    patient = Patient.query.get_or_404(patient_id)
    patient.pat_name = data.get('pat_name', patient.pat_name)
    patient.gender = data.get('gender', patient.gender)
    patient.contact_num = data.get('contact_num', patient.contact_num)
    
    dob_str = data.get('dob')
    if dob_str:
        patient.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
    db.session.flush()
    log_audit("UPDATE_PATIENT", "Patient", patient.patient_id)
    db.session.commit()
    return patient

def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id:
        user = User.query.get(patient.user_id)
        patient.user_id = None
        db.session.flush()
        if user:
            db.session.delete(user)
        
    future_appts = Appointment.query.filter(
        Appointment.patient_id == patient_id, 
        Appointment.date >= date.today(), 
        Appointment.status != 'Cancelled'
    ).all()
    for appt in future_appts:
        appt.status = 'Cancelled'
        if appt.treatment:
            db.session.delete(appt.treatment)
            
    log_audit("DELETE_PATIENT", "Patient", patient_id)
    db.session.commit()

def admin_book_appointment(patient_id, doctor_id, selected_date, selected_time):
    patient = Patient.query.get_or_404(patient_id)
    if not patient.user_id:
        raise ValueError("Cannot schedule appointment for an inactive patient.")
        
    if selected_date < date.today():
        raise ValueError("Cannot book appointments in the past.")

    valid_slot = Availability.query.filter_by(
        doctor_id=doctor_id,
        date=selected_date,
        start_time=selected_time
    ).first()

    if not valid_slot:
        raise ValueError(f"Invalid Slot! Doctor is not available at {selected_time.strftime('%I:%M %p')} on this date.")

    current_count = Appointment.query.filter_by(
        doctor_id=doctor_id, 
        date=selected_date, 
        time=selected_time
    ).filter(Appointment.status != 'Cancelled').count()

    if current_count >= MAX_APPOINTMENTS_PER_SLOT:
        raise ValueError(f"Slot at {selected_time.strftime('%I:%M %p')} is fully booked (Max {MAX_APPOINTMENTS_PER_SLOT}).")
        
    new_token = current_count + 1

    new_appt = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=selected_date,
        time=selected_time,
        status='Booked',
        token_number=new_token
    )
    
    db.session.add(new_appt)
    db.session.flush()
    log_audit("ADMIN_BOOK_APPOINTMENT", "Appointment", new_appt.appointment_id, {
        "patient_id": patient_id,
        "doctor_id": doctor_id
    })
    db.session.commit()
    return new_appt
