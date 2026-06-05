from flask import Blueprint, request, jsonify, current_app
from models import Doctor, Patient, Treatment, Appointment, Availability
from flask_login import login_required, current_user
from extensions import db
from datetime import datetime, date
from .utils import role_required, validate_date, sanitize_string
from services import doctor_service

doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/v1/doctor')

@doctor_bp.route('/', methods=['GET'])
@role_required('doctor')
def doctor_dashboard():
    doctor = Doctor.query.filter_by(user_id=current_user.user_id).first_or_404()
    
    appointments = Appointment.query.filter_by(doctor_id=doctor.doctor_id).order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).all()
    
    appt_data = [{
        "appointment_id": a.appointment_id,
        "date": str(a.date),
        "time": str(a.time),
        "status": a.status,
        "patient_name": a.patient.pat_name,
        "patient_id": a.patient_id,
        "notes": a.treatment.notes if a.treatment else ""
    } for a in appointments]

    return jsonify({"doctor": {"name": doctor.doc_name}, "appointments": appt_data, "status": "success"})

@doctor_bp.route('/add_treatment/<int:appointment_id>', methods=['POST'])
@role_required('doctor')
def add_treatment(appointment_id):
    data = request.get_json()
    if not data:
         return jsonify({"message": "Invalid data", "status": "error"}), 400

    try:
        validated_data = {
            'ailment': sanitize_string(data.get('ailment'), min_len=2, max_len=200, field_name="Ailment"),
            'prescription': sanitize_string(data.get('prescription'), min_len=2, max_len=1000, field_name="Prescription"),
            'notes': sanitize_string(data.get('notes'), min_len=0, max_len=1000, field_name="Notes")
        }
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400

    try:
        doctor_service.add_patient_treatment(
            current_user.user_id,
            appointment_id,
            validated_data['ailment'],
            validated_data['prescription'],
            validated_data['notes']
        )
        current_app.logger.warning(f"Doctor added treatment details for appointment ID {appointment_id}")
        return jsonify({"message": "Treatment added", "status": "success"})
    except PermissionError as perm_err:
        return jsonify({"message": str(perm_err), "status": "error"}), 403
    except Exception as e:
        current_app.logger.error(f"Error adding treatment: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}", "status": "error"}), 500

@doctor_bp.route('/view_treatment/<int:appointment_id>')
@role_required('doctor')
def view_treatment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    treatments = Treatment.query.filter_by(appointment_id=appointment_id).all()
    
    return jsonify({
        "status": "success",
        "doctor": {"name": appointment.doctor.doc_name},
        "patient": {"name": appointment.patient.pat_name, "id": appointment.patient_id},
        "appointment": {"date": str(appointment.date), "time": str(appointment.time), "status": appointment.status},
        "treatments": [{"ailment": t.ailment, "prescription": t.prescription, "notes": t.notes} for t in treatments]
    })

@doctor_bp.route('/patient_history/<int:patient_id>')
@role_required('doctor')
def patient_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc()).all()

    appt_data = [{
        "appointment_id": a.appointment_id,
        "date": str(a.date),
        "time": str(a.time),
        "status": a.status,
        "doctor_name": a.doctor.doc_name,
        "token": a.token_number
    } for a in appointments]

    return jsonify({
        "status": "success",
        "patient": {"name": patient.pat_name, "age": patient.age, "gender": patient.gender},
        "appointments": appt_data
    })

@doctor_bp.route('/set_availability', methods=['GET', 'POST'])
@role_required('doctor')
def set_availability():
    doctor = Doctor.query.filter_by(user_id=current_user.user_id).first_or_404()
    
    if request.method == 'GET':
        slots = Availability.query.filter_by(doctor_id=doctor.doctor_id).order_by(Availability.date, Availability.start_time).all()
        slots_data = [{"slot_id": s.id, "date": str(s.date), "start_time": str(s.start_time), "end_time": str(s.end_time)} for s in slots]
        return jsonify({"slots": slots_data, "status": "success"})

    # POST logic
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    try:
        selected_date = validate_date(data.get('date'), field_name="Availability Date")
        time_slot = sanitize_string(data.get('time_slot'), min_len=2, max_len=10, field_name="Time Slot")
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400

    try:
        new_slot, status = doctor_service.create_availability_slot(current_user.user_id, selected_date, time_slot)
        if status == "warning":
            return jsonify({"message": "This time slot is already set.", "status": "warning"})
        
        current_app.logger.warning(f"Doctor ID {doctor.doctor_id} set availability for {selected_date} at {time_slot}")
        return jsonify({"message": "Availability added!", "status": "success"})
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400
    except Exception as e:
        current_app.logger.error(f"Error setting availability: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}", "status": "error"}), 500

@doctor_bp.route('/remove_slot/<int:slot_id>', methods=['DELETE'])
@role_required('doctor')
def remove_slot(slot_id):
    try:
        doctor_service.remove_availability_slot(current_user.user_id, slot_id)
        current_app.logger.warning(f"Doctor removed availability slot ID {slot_id}")
        return jsonify({"message": "Slot removed successfully!", "status": "success"})
    except PermissionError as perm_err:
        return jsonify({"message": str(perm_err), "status": "error"}), 403
    except ValueError as val_err:
        return jsonify({"message": str(val_err), "status": "error"}), 400
    except Exception as e:
        current_app.logger.error(f"Error removing availability slot: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}", "status": "error"}), 500