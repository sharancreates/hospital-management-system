from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date
from flask_login import login_required
from .utils import role_required, validate_email, validate_phone, validate_age, validate_date, sanitize_string
from extensions import db
from models import Patient, User, Department, Doctor, Appointment, Availability, MAX_APPOINTMENTS_PER_SLOT
from services import admin_service

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@admin_bp.route('/', methods=['GET'])
@role_required('admin')
def admin_dashboard():
    # Keep simple view-query in controller
    patients_count = Patient.query.filter(Patient.user_id.isnot(None)).count()
    doctors_count = Doctor.query.filter(Doctor.user_id.isnot(None)).count()
    appointments_count = Appointment.query.filter(Appointment.status != 'Cancelled').count()
    recent_appointments = Appointment.query.options(
        db.joinedload(Appointment.patient),
        db.joinedload(Appointment.doctor)
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).limit(5).all()

    recent_data = [{
        "appointment_id": appt.appointment_id,
        "patient_name": appt.patient.pat_name if appt.patient else "Unknown",
        "doctor_name": appt.doctor.doc_name if appt.doctor else "Unknown",
        "date": str(appt.date),
        "time": str(appt.time),
        "status": appt.status
    } for appt in recent_appointments]

    # Query all lists expected by frontend client-side tables
    doctors = Doctor.query.filter(Doctor.user_id.isnot(None)).all()
    patients = Patient.query.filter(Patient.user_id.isnot(None)).all()
    appointments = Appointment.query.all()
    departments = Department.query.all()

    doctors_data = [{
        "doctor_id": d.doctor_id,
        "doc_name": d.doc_name,
        "department": d.department.department_name if d.department else "N/A",
        "gender": d.gender,
        "dob": str(d.dob),
        "contact_num": d.contact_num
    } for d in doctors]

    patients_data = [{
        "patient_id": p.patient_id,
        "pat_name": p.pat_name,
        "email": p.user.email if p.user else "N/A",
        "gender": p.gender,
        "dob": str(p.dob),
        "age": p.age,
        "contact_num": p.contact_num
    } for p in patients]

    appointments_data = [{
        "appointment_id": a.appointment_id,
        "patient_name": a.patient.pat_name if a.patient else "N/A",
        "doctor_name": a.doctor.doc_name if a.doctor else "N/A",
        "date": str(a.date),
        "time": str(a.time),
        "status": a.status
    } for a in appointments]

    departments_data = [{
        "department_id": d.department_id,
        "department_name": d.department_name
    } for d in departments]

    # Query analytics
    from sqlalchemy import func
    appts_by_date = db.session.query(
        Appointment.date, 
        func.count(Appointment.appointment_id)
    ).filter(
        Appointment.status != 'Cancelled', 
        Appointment.date <= date.today()
    ).group_by(Appointment.date).order_by(Appointment.date.desc()).limit(7).all()

    trend = [{"date": str(row[0]), "appointments": row[1]} for row in reversed(appts_by_date)]

    departments_chart = []
    for d in departments:
        doc_count = Doctor.query.filter_by(department_id=d.department_id).filter(Doctor.user_id.isnot(None)).count()
        departments_chart.append({"name": d.department_name, "value": doc_count})

    analytics = {
        "trend": trend,
        "departments": departments_chart
    }

    return jsonify({
        "stats": {
            "patients": patients_count,
            "doctors": doctors_count,
            "appointments": appointments_count
        },
        "recent_appointments": recent_data,
        "doctors": doctors_data,
        "patients": patients_data,
        "appointments": appointments_data,
        "departments": departments_data,
        "analytics": analytics,
        "status": "success"
    })

@admin_bp.route("/add_doctor", methods=['POST'])
@role_required('admin')
def add_doctor():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    try:
        validated_data = {
            'doc_name': sanitize_string(data.get('doc_name'), min_len=2, max_len=100, field_name="Doctor Name"),
            'gender': sanitize_string(data.get('gender'), min_len=2, max_len=10, field_name="Gender"),
            'contact_num': validate_phone(data.get('contact_num')),
            'specialization': int(data.get('specialization')),
            'dob': str(validate_date(data.get('dob'), field_name="Date of Birth"))
        }
    except (ValueError, TypeError) as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400

    try:
        doctor, email = admin_service.create_doctor(validated_data)
        current_app.logger.warning(f"Admin created doctor account for {email}")
        return jsonify({
            "message": "Doctor added successfully! A welcome email containing credentials has been sent.", 
            "status": "success", 
            "email": email
        })
    except Exception as e:
        current_app.logger.error(f"Error adding doctor: {str(e)}")
        return jsonify({"message": f"Error adding doctor: {str(e)}", "status": "error"}), 500

@admin_bp.route("/update_doctor/<int:doctor_id>", methods=['POST'])
@role_required('admin')
def update_doctor(doctor_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    try:
        validated_data = {}
        if 'doc_name' in data:
            validated_data['doc_name'] = sanitize_string(data.get('doc_name'), min_len=2, max_len=100, field_name="Doctor Name")
        if 'gender' in data:
            validated_data['gender'] = sanitize_string(data.get('gender'), min_len=2, max_len=10, field_name="Gender")
        if 'contact_num' in data:
            validated_data['contact_num'] = validate_phone(data.get('contact_num'))
        if 'specialization' in data:
            validated_data['specialization'] = int(data.get('specialization'))
        if 'dob' in data:
            validated_data['dob'] = str(validate_date(data.get('dob'), field_name="Date of Birth"))
    except (ValueError, TypeError) as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400

    try:
        admin_service.update_doctor(doctor_id, validated_data)
        return jsonify({"message": "Doctor updated successfully", "status": "success"})
    except Exception as e:
        current_app.logger.error(f"Error updating doctor {doctor_id}: {str(e)}")
        return jsonify({"message": f"Error updating doctor: {str(e)}", "status": "error"}), 500

@admin_bp.route("/delete_doctor/<int:doctor_id>", methods=['DELETE'])
@role_required('admin')
def delete_doctor(doctor_id):
    try:
        admin_service.delete_doctor(doctor_id)
        current_app.logger.warning(f"Admin deactivated doctor ID {doctor_id}")
        return jsonify({"message": "Doctor deleted", "status": "success"})
    except Exception as e:
        current_app.logger.error(f"Error deleting doctor {doctor_id}: {str(e)}")
        return jsonify({"message": f"Error deleting doctor: {str(e)}", "status": "error"}), 500

@admin_bp.route('/add_patient', methods=['POST'])
@role_required('admin')
def add_patient():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    try:
        validated_data = {
            'pat_name': sanitize_string(data.get('pat_name'), min_len=2, max_len=100, field_name="Patient Name"),
            'gender': sanitize_string(data.get('gender'), min_len=2, max_len=10, field_name="Gender"),
            'contact_num': validate_phone(data.get('contact_num')),
            'age': validate_age(data.get('age')),
            'email': validate_email(data.get('email')),
            'dob': str(validate_date(data.get('dob'), field_name="Date of Birth"))
        }
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400

    try:
        admin_service.create_patient(validated_data)
        current_app.logger.warning(f"Admin registered new patient: {validated_data['email']}")
        return jsonify({
            "message": "Patient added successfully! A welcome email containing credentials has been sent.", 
            "status": "success", 
            "email": validated_data['email']
        })
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding patient: {str(e)}")
        return jsonify({"message": f"Error adding patient: {str(e)}", "status": "error"}), 500

@admin_bp.route('/update_patient/<int:patient_id>', methods=['POST'])
@role_required('admin')
def update_patient(patient_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    try:
        validated_data = {}
        if 'pat_name' in data:
            validated_data['pat_name'] = sanitize_string(data.get('pat_name'), min_len=2, max_len=100, field_name="Patient Name")
        if 'gender' in data:
            validated_data['gender'] = sanitize_string(data.get('gender'), min_len=2, max_len=10, field_name="Gender")
        if 'contact_num' in data:
            validated_data['contact_num'] = validate_phone(data.get('contact_num'))
        if 'age' in data:
            validated_data['age'] = validate_age(data.get('age'))
        if 'dob' in data:
            validated_data['dob'] = str(validate_date(data.get('dob'), field_name="Date of Birth"))
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400

    try:
        admin_service.update_patient(patient_id, validated_data)
        return jsonify({"message": "Patient updated successfully", "status": "success"})
    except Exception as e:
        current_app.logger.error(f"Error updating patient {patient_id}: {str(e)}")
        return jsonify({"message": f"Error updating patient: {str(e)}", "status": "error"}), 500

@admin_bp.route("/delete_patient/<int:patient_id>", methods=['DELETE'])
@role_required('admin')
def delete_patient(patient_id):
    try:
        admin_service.delete_patient(patient_id)
        current_app.logger.warning(f"Admin deactivated patient ID {patient_id}")
        return jsonify({"message": "Patient deleted", "status": "success"})
    except Exception as e:
        current_app.logger.error(f"Error deleting patient {patient_id}: {str(e)}")
        return jsonify({"message": f"Error deleting patient: {str(e)}", "status": "error"}), 500

@admin_bp.route('/get_slots/<int:doctor_id>/<string:date_str>')
@role_required('admin')
def get_slots(doctor_id, date_str):
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        all_availability = Availability.query.filter_by(
            doctor_id=doctor_id,
            date=selected_date
        ).order_by(Availability.start_time).all()

        available_times = []
        for slot in all_availability:
            booked_count = Appointment.query.filter_by(
                doctor_id=doctor_id,
                date=selected_date,
                time=slot.start_time
            ).filter(Appointment.status != 'Cancelled').count()

            if booked_count < MAX_APPOINTMENTS_PER_SLOT:
                time_str = slot.start_time.strftime("%H:%M") 
                available_times.append({
                    "time": time_str,
                    "display": slot.start_time.strftime("%I:%M %p"), 
                    "remaining": MAX_APPOINTMENTS_PER_SLOT - booked_count
                })
        
        return jsonify({"slots": available_times})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@admin_bp.route('/set_appointment', methods=['POST'])
@role_required('admin')
def set_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    doctor_id = data.get('doctor_id')
    patient_id = data.get('patient_id')
    selected_date_str = data.get('date')
    selected_time_str = data.get('time')
    
    if not (doctor_id and patient_id and selected_date_str and selected_time_str):
        return jsonify({"message": "Missing required fields", "status": "error"}), 400

    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        selected_time = datetime.strptime(selected_time_str, "%H:%M").time()
    except ValueError:
        return jsonify({"message": "Invalid date/time format", "status": "error"}), 400

    try:
        appt = admin_service.admin_book_appointment(patient_id, doctor_id, selected_date, selected_time)
        current_app.logger.warning(f"Admin booked appointment ID {appt.appointment_id} for Patient {patient_id}")
        return jsonify({"message": f"Appointment scheduled successfully! Token: {appt.token_number}", "status": "success"})
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400
    except Exception as e:
        current_app.logger.error(f"Error booking appointment: {str(e)}")
        return jsonify({"message": f"Database error: {str(e)}", "status": "error"}), 500

@admin_bp.route('/delete_appointment/<int:appointment_id>', methods=['DELETE'])
@role_required('admin')
def delete_appointment(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    try:
        appt.status = 'Cancelled'
        if appt.treatment:
            db.session.delete(appt.treatment)
        db.session.commit()
        current_app.logger.warning(f"Admin cancelled appointment ID {appointment_id}")
        return jsonify({"message": "Appointment cancelled successfully", "status": "success"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling appointment {appointment_id}: {str(e)}")
        return jsonify({"message": f"Error cancelling appointment: {str(e)}", "status": "error"}), 500

@admin_bp.route('/doctor_profile/<int:doctor_id>', methods=['GET'])
@role_required('admin')
def get_doctor_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    total_appts = Appointment.query.filter_by(doctor_id=doctor_id).count()
    treated_appts = Appointment.query.filter_by(doctor_id=doctor_id, status='Completed').count()
    
    return jsonify({
        "doctor": {
            "doc_name": doctor.doc_name,
            "department": doctor.department.department_name if doctor.department else "N/A",
            "gender": doctor.gender,
            "dob": str(doctor.dob),
            "contact_num": doctor.contact_num
        },
        "stats": {
            "total_appointments": total_appts,
            "total_treated": treated_appts
        },
        "status": "success"
    })

@admin_bp.route('/patient_profile/<int:patient_id>', methods=['GET'])
@role_required('admin')
def get_patient_profile(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appts = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc()).all()
    
    history = []
    for a in appts:
        t = a.treatment
        history.append({
            "date": str(a.date),
            "doctor": a.doctor.doc_name,
            "status": a.status,
            "ailment": t.ailment if t else "N/A",
            "prescription": t.prescription if t else "N/A",
            "notes": t.notes if t else "N/A"
        })
        
    return jsonify({
        "patient": {
            "pat_name": patient.pat_name,
            "email": patient.user.email if patient.user else None,
            "gender": patient.gender,
            "dob": str(patient.dob),
            "age": patient.age,
            "contact_num": patient.contact_num
        },
        "history": history,
        "status": "success"
    })

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_dashboard_stats():
    total_doctors = Doctor.query.filter(Doctor.user_id.isnot(None)).count()
    total_patients = Patient.query.filter(Patient.user_id.isnot(None)).count()
    total_appointments = Appointment.query.filter(Appointment.status != 'Cancelled').count()
    completed_appointments = Appointment.query.filter_by(status='Completed').count()
    pending_appointments = Appointment.query.filter_by(status='Booked').count()

    return jsonify({
        "doctors": total_doctors,
        "patients": total_patients,
        "appointments": total_appointments,
        "completed": completed_appointments,
        "pending": pending_appointments,
        "status": "success"
    })

@admin_bp.route('/appointment_analytics', methods=['GET'])
@role_required('admin')
def get_analytics():
    # Simple line stats for last 7 days
    from sqlalchemy import func
    appts_by_date = db.session.query(
        Appointment.date, 
        func.count(Appointment.appointment_id)
    ).filter(
        Appointment.status != 'Cancelled', 
        Appointment.date <= date.today()
    ).group_by(Appointment.date).order_by(Appointment.date.desc()).limit(7).all()

    timeline = [{"date": str(row[0]), "count": row[1]} for row in reversed(appts_by_date)]

    # Department distribution
    depts = Department.query.all()
    dept_distribution = []
    for d in depts:
        doc_ids = [doc.doctor_id for doc in d.doctors]
        count = Appointment.query.filter(
            Appointment.doctor_id.in_(doc_ids) if doc_ids else False,
            Appointment.status != 'Cancelled'
        ).count()
        dept_distribution.append({"department": d.department_name, "count": count})

    return jsonify({
        "timeline": timeline,
        "department_distribution": dept_distribution,
        "status": "success"
    })

from sqlalchemy.orm import joinedload

@admin_bp.route('/doctors', methods=['GET'])
@role_required('admin')
def get_doctors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    
    query = Doctor.query.options(joinedload(Doctor.department)).filter(Doctor.user_id.isnot(None))
    if search:
        query = query.filter(Doctor.doc_name.ilike(f"%{search}%"))
        
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    doctors = pagination.items
    
    data = [{
        "doctor_id": d.doctor_id,
        "doc_name": d.doc_name,
        "department": d.department.department_name if d.department else "N/A",
        "gender": d.gender,
        "dob": str(d.dob),
        "contact_num": d.contact_num
    } for d in doctors]
    
    return jsonify({
        "doctors": data,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "status": "success"
    })

@admin_bp.route('/patients', methods=['GET'])
@role_required('admin')
def get_patients():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    
    query = Patient.query.options(joinedload(Patient.user)).filter(Patient.user_id.isnot(None))
    if search:
        query = query.filter(Patient.pat_name.ilike(f"%{search}%"))
        
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    patients = pagination.items
    
    data = [{
        "patient_id": p.patient_id,
        "pat_name": p.pat_name,
        "email": p.user.email if p.user else "N/A",
        "gender": p.gender,
        "dob": str(p.dob),
        "age": p.age,
        "contact_num": p.contact_num
    } for p in patients]
    
    return jsonify({
        "patients": data,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "status": "success"
    })

@admin_bp.route('/appointments', methods=['GET'])
@role_required('admin')
def get_appointments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Appointment.query.options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor)
    ).order_by(Appointment.date.desc(), Appointment.time.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    appointments = pagination.items
    
    data = [{
        "appointment_id": a.appointment_id,
        "patient_name": a.patient.pat_name if a.patient else "N/A",
        "doctor_name": a.doctor.doc_name if a.doctor else "N/A",
        "date": str(a.date),
        "time": str(a.time),
        "status": a.status
    } for a in appointments]
    
    return jsonify({
        "appointments": data,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "status": "success"
    })