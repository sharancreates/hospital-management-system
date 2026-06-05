from flask import Blueprint, request, jsonify, current_app
from models import Patient, User, Doctor, Department, Appointment, Treatment, Availability
from datetime import datetime, date
from extensions import db, limiter
from flask_login import current_user, login_required
from .utils import role_required, validate_email, validate_phone, validate_age, validate_date, sanitize_string, validate_password_complexity
from services import patient_service

patient_bp = Blueprint('patient', __name__, url_prefix='/api/v1/patient')

def get_current_patient():
    return Patient.query.filter_by(user_id=current_user.user_id).first()

@patient_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    if current_user.is_authenticated:
        return {"message": "Already logged in", "status": "info"}

    data = request.get_json()
    if not data:
        return {"message": "Invalid data", "status": "error"}, 400

    try:
        is_ok, err_msg = validate_password_complexity(data.get('password'))
        if not is_ok:
            raise ValueError(err_msg)
            
        validated_data = {
            'email': validate_email(data.get('email')),
            'password': sanitize_string(data.get('password'), min_len=8, max_len=100, field_name="Password"),
            'pat_name': sanitize_string(data.get('pat_name'), min_len=2, max_len=100, field_name="Patient Name"),
            'gender': sanitize_string(data.get('gender'), min_len=2, max_len=10, field_name="Gender"),
            'dob': str(validate_date(data.get('dob'), field_name="Date of Birth")),
            'contact_num': validate_phone(data.get('contact_num')),
            'age': validate_age(data.get('age'))
        }
    except ValueError as val_err:
        return {"message": str(val_err), "status": "error"}, 400

    try:
        patient_service.register_patient(
            validated_data['email'],
            validated_data['password'],
            validated_data['pat_name'],
            validated_data['gender'],
            validated_data['dob'],
            validated_data['contact_num'],
            validated_data['age']
        )
        current_app.logger.warning(f"New patient self-registration: {validated_data['email']}")
        return {"message": "Registration successful", "status": "success"}, 201
    except ValueError as val_err:
        return {"message": str(val_err), "status": "error"}, 400
    except Exception as e:
        current_app.logger.error(f"Error during registration: {str(e)}")
        return {"message": f"Error during registration: {str(e)}", "status": "error"}, 500

@patient_bp.route('/dashboard', methods=['GET'])
@role_required('patient')
def patient_dashboard():
    patient = get_current_patient()
    if not patient:
        return jsonify({"message": "Patient profile not found", "status": "error"}), 404

    appointments = Appointment.query.filter_by(patient_id=patient.patient_id).order_by(Appointment.date.desc()).all()
    docs = Doctor.query.filter(Doctor.user_id.isnot(None)).all()
    departments = Department.query.all()
    
    appt_data = [{
        "appointment_id": a.appointment_id,
        "date": str(a.date),
        "time": str(a.time),
        "status": a.status,
        "doctor_name": a.doctor.doc_name,
        "token": a.token_number,
        "treatment_id": a.treatment.treatment_id if a.treatment else None
    } for a in appointments]

    docs_data = [{"doctor_id": d.doctor_id, "doc_name": d.doc_name, "department": d.department.department_name if d.department else "N/A"} for d in docs]
    dept_data = [{"department_id": d.department_id, "department_name": d.department_name} for d in departments]

    patient_data = {
        "pat_name": patient.pat_name,
        "patient_id": patient.patient_id,
        "email": current_user.email,
        "contact_num": patient.contact_num,
        "age": patient.age,
        "gender": patient.gender,
        "dob": str(patient.dob)
    }

    return jsonify({
        "patient": patient_data,
        "appointments": appt_data,
        "doctors": docs_data,
        "departments": dept_data,
        "status": "success"
    })

@patient_bp.route('/update_patient', methods=['POST'])
@role_required('patient')
def update_patient():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    try:
        pat_name = sanitize_string(data.get('pat_name'), min_len=2, max_len=100, field_name="Patient Name") if 'pat_name' in data else None
        gender = sanitize_string(data.get('gender'), min_len=2, max_len=10, field_name="Gender") if 'gender' in data else None
        contact_num = validate_phone(data.get('contact_num')) if 'contact_num' in data else None
        dob_str = str(validate_date(data.get('dob'), field_name="Date of Birth")) if 'dob' in data else None
        age = validate_age(data.get('age')) if 'age' in data else None
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400

    try:
        patient_service.update_patient_profile(
            current_user.user_id,
            pat_name,
            gender,
            contact_num,
            dob_str,
            age
        )
        return jsonify({"message": "Profile updated successfully.", "status": "success"})
    except Exception as e:
        current_app.logger.error(f"Error updating profile for user ID {current_user.user_id}: {str(e)}")
        return jsonify({"message": f"Error updating profile: {str(e)}", "status": "error"}), 500

@patient_bp.route('/treatment/<int:treatment_id>')
@role_required('patient')
def view_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    appointment = treatment.appointment
    current_pat = get_current_patient()
    
    if not appointment or appointment.patient_id != current_pat.patient_id:
        return jsonify({"message": "Forbidden", "status": "error"}), 403

    return jsonify({
        "status": "success",
        "doctor": {"name": appointment.doctor.doc_name},
        "patient": {"name": appointment.patient.pat_name},
        "appointment": {"date": str(appointment.date), "time": str(appointment.time), "status": appointment.status},
        "treatment": {
            "ailment": treatment.ailment,
            "prescription": treatment.prescription,
            "notes": treatment.notes,
            "doctor_name": appointment.doctor.doc_name,
            "date": str(appointment.date)
        }
    })

@patient_bp.route("/add_appointment", methods=["POST"])
@role_required('patient')
def add_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    selected_doctor = data.get("doc")
    selected_date = data.get("date")
    slot_start_time_str = data.get("time") 

    if not (selected_doctor and selected_date and slot_start_time_str):
        return jsonify({"message": "Missing fields", "status": "error"}), 400

    try:
        appt, token = patient_service.patient_book_appointment(
            current_user.user_id,
            selected_doctor,
            selected_date,
            slot_start_time_str
        )
        current_app.logger.warning(f"Patient booked appointment ID {appt.appointment_id}. Token: {token}")
        return jsonify({"message": f"Appointment Booked! Token: {token}", "status": "success", "token": token})
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400
    except Exception as e:
        current_app.logger.error(f"Error booking appointment for user ID {current_user.user_id}: {str(e)}")
        return jsonify({"message": f"Error booking: {str(e)}", "status": "error"}), 500

@patient_bp.route('/cancel_appointment/<int:appointment_id>', methods=['DELETE'])
@role_required('patient')
def cancel_appointment(appointment_id):
    try:
        patient_service.cancel_patient_appointment(current_user.user_id, appointment_id)
        current_app.logger.warning(f"Patient cancelled appointment ID {appointment_id}")
        return jsonify({"message": "Appointment cancelled", "status": "success"})
    except PermissionError as perm_err:
        return jsonify({"message": str(perm_err), "status": "error"}), 403
    except Exception as e:
        current_app.logger.error(f"Error cancelling appointment {appointment_id}: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}", "status": "error"}), 500

@patient_bp.route('/doc_profile/<int:doctor_id>')
@role_required('patient')
def doc_profile(doctor_id):
    from models import MAX_APPOINTMENTS_PER_SLOT
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.user_id is None:
        return jsonify({"message": "Doctor is not active.", "status": "error"}), 404
    all_slots = Availability.query.filter(
        Availability.doctor_id == doctor_id,
        Availability.date >= date.today()
    ).order_by(Availability.date, Availability.start_time).all()

    free_slots = []
    for slot in all_slots:
        booked_count = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=slot.date,
            time=slot.start_time
        ).filter(Appointment.status != 'Cancelled').count()
        if booked_count < MAX_APPOINTMENTS_PER_SLOT:
            free_slots.append({
                "date": str(slot.date),
                "start_time": str(slot.start_time),
                "end_time": str(slot.end_time)
            })

    return jsonify({
        "status": "success",
        "doctor": {"name": doctor.doc_name, "department": doctor.department.department_name if doctor.department else "N/A"},
        "free_slots": free_slots
    })

@patient_bp.route('/queue_status/<int:appointment_id>')
@role_required('patient')
def queue_status(appointment_id):
    app = Appointment.query.get_or_404(appointment_id)
    current_pat = get_current_patient()
    if app.patient_id != current_pat.patient_id:
        return jsonify({"message": "Forbidden", "status": "error"}), 403

    people_ahead = Appointment.query.filter(
        Appointment.doctor_id == app.doctor_id,
        Appointment.date == app.date,
        Appointment.time == app.time,
        Appointment.token_number < app.token_number,
        Appointment.status == 'Booked'
    ).count()

    return jsonify({
        "status": "success",
        "token_number": app.token_number,
        "people_ahead": people_ahead,
        "estimated_wait_minutes": people_ahead * 15
    })