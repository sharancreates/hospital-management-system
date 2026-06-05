from models import Patient, User, Doctor, Appointment, Availability, MAX_APPOINTMENTS_PER_SLOT
from extensions import db, socketio
from datetime import datetime, date
from werkzeug.security import generate_password_hash
from sqlalchemy import text
from services.audit_service import log_audit

def register_patient(email, password, pat_name, gender, dob_str, contact_num, age):
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already exists")

    hashed_pw = generate_password_hash(password)
    user = User(email=email, password_hash=hashed_pw, role='patient')
    db.session.add(user)
    db.session.flush()

    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

    # Patient has no age database column anymore (computed dynamically via dob)
    patient = Patient(
        pat_name=pat_name,
        gender=gender,
        dob=dob_date,
        contact_num=contact_num,
        user_id=user.user_id
    )
    db.session.add(patient)
    db.session.flush()
    log_audit("REGISTER_PATIENT", "Patient", patient.patient_id, {"email": email})
    db.session.commit()
    return patient

def update_patient_profile(user_id, pat_name, gender, contact_num, dob_str, age):
    patient = Patient.query.filter_by(user_id=user_id).first_or_404()
    
    patient.pat_name = pat_name or patient.pat_name
    patient.gender = gender or patient.gender
    patient.contact_num = contact_num or patient.contact_num
    
    if dob_str:
        patient.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
    db.session.flush()
    log_audit("UPDATE_PATIENT_PROFILE", "Patient", patient.patient_id)
    db.session.commit()
    return patient

def patient_book_appointment(user_id, selected_doctor, selected_date, slot_start_time_str):
    patient = Patient.query.filter_by(user_id=user_id).first_or_404()
    
    doc = Doctor.query.get(selected_doctor)
    if not doc or doc.user_id is None:
        raise ValueError("Doctor is no longer active.")

    date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    if date_obj < date.today():
        raise ValueError("Cannot book in the past.")

    start_time_obj = datetime.strptime(slot_start_time_str, "%H:%M").time()

    slot = Availability.query.filter_by(
        doctor_id=selected_doctor,
        date=date_obj,
        start_time=start_time_obj
    ).first()

    if not slot:
        raise ValueError("Invalid slot or doctor mismatch.")

    # Check if the patient already has an appointment at this time
    existing_patient_appt = Appointment.query.filter_by(
        patient_id=patient.patient_id,
        date=date_obj,
        time=start_time_obj
    ).filter(Appointment.status != 'Cancelled').first()

    if existing_patient_appt:
        raise ValueError("You already have an appointment booked at this exact time.")

    current_count = Appointment.query.filter_by(
        doctor_id=selected_doctor, 
        date=date_obj, 
        time=start_time_obj
    ).filter(Appointment.status != 'Cancelled').count()

    if current_count >= MAX_APPOINTMENTS_PER_SLOT:
        raise ValueError("Slot filled up.")
        
    new_token = current_count + 1
    new_app = Appointment(
        patient_id=patient.patient_id,
        doctor_id=selected_doctor,
        date=date_obj,
        time=start_time_obj,
        status="Booked",
        token_number=new_token
    )
    db.session.add(new_app)
    db.session.flush()
    log_audit("BOOK_APPOINTMENT", "Appointment", new_app.appointment_id, {
        "doctor_id": selected_doctor,
        "token": new_token
    })
    db.session.commit()
    try:
        socketio.emit('queue_update', {'event': 'book', 'doctor_id': selected_doctor})
    except Exception:
        pass
    return new_app, new_token

def cancel_patient_appointment(user_id, appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.filter_by(user_id=user_id).first_or_404()
    
    if appt.patient_id != patient.patient_id:
        raise PermissionError("Unauthorized: You do not own this appointment.")

    appt.status = 'Cancelled'
    if appt.treatment:
        db.session.delete(appt.treatment)
        
    log_audit("CANCEL_APPOINTMENT", "Appointment", appointment_id)
    db.session.commit()
    try:
        socketio.emit('queue_update', {'event': 'cancel', 'doctor_id': appt.doctor_id})
    except Exception:
        pass
