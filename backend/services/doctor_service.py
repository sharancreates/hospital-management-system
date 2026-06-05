from models import Doctor, Appointment, Availability, Treatment, Patient
from extensions import db, socketio
from datetime import datetime, date
from services.audit_service import log_audit

def add_patient_treatment(doctor_user_id, appointment_id, ailment, prescription, notes):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor_record = Doctor.query.filter_by(user_id=doctor_user_id).first_or_404()
    
    if appointment.doctor_id != doctor_record.doctor_id:
        raise PermissionError("Unauthorized: Appointment is not assigned to this doctor.")

    treatment = Treatment(
        ailment=ailment,
        prescription=prescription,
        notes=notes,
        appointment_id=appointment_id,
        date=appointment.date
    )
    appointment.status = "Completed"
    db.session.add(treatment)
    db.session.flush()
    log_audit("ADD_TREATMENT", "Treatment", treatment.treatment_id, {"appointment_id": appointment_id})
    db.session.commit()
    try:
        socketio.emit('queue_update', {'event': 'complete', 'doctor_id': appointment.doctor_id})
    except Exception:
        pass
    return treatment

def create_availability_slot(doctor_user_id, selected_date, start_time_str):
    doctor = Doctor.query.filter_by(user_id=doctor_user_id).first_or_404()
    
    TIME_SLOTS = {
        "09:00": "11:00",
        "11:00": "13:00",
        "13:00": "15:00",
        "15:00": "17:00",
        "17:00": "19:00",
        "19:00": "21:00"
    }

    if selected_date < date.today():
        raise ValueError("Cannot set availability in the past.")

    if start_time_str not in TIME_SLOTS:
        raise ValueError("Invalid time slot selection.")

    start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
    end_time_str = TIME_SLOTS[start_time_str]
    end_time_obj = datetime.strptime(end_time_str, "%H:%M").time()

    exists = Availability.query.filter_by(
        doctor_id=doctor.doctor_id,
        date=selected_date,
        start_time=start_time_obj
    ).first()

    if exists:
        return None, "warning"

    new_slot = Availability(
        doctor_id=doctor.doctor_id,
        date=selected_date,
        start_time=start_time_obj,
        end_time=end_time_obj
    )
    db.session.add(new_slot)
    db.session.flush()
    log_audit("CREATE_AVAILABILITY", "Availability", new_slot.id, {
        "doctor_id": doctor.doctor_id,
        "date": str(selected_date),
        "start_time": start_time_str
    })
    db.session.commit()
    return new_slot, "success"

def remove_availability_slot(doctor_user_id, slot_id):
    slot = Availability.query.get_or_404(slot_id)
    doctor_record = Doctor.query.filter_by(user_id=doctor_user_id).first_or_404()
    
    if slot.doctor_id != doctor_record.doctor_id:
        raise PermissionError("Unauthorized action.")

    has_bookings = Appointment.query.filter_by(
        doctor_id=slot.doctor_id,
        date=slot.date,
        time=slot.start_time
    ).filter(Appointment.status != 'Cancelled').first()

    if has_bookings:
        raise ValueError("Cannot remove slot with active appointments. Please reschedule or cancel the appointments first.")

    log_audit("DELETE_AVAILABILITY", "Availability", slot_id, {
        "doctor_id": doctor_record.doctor_id,
        "date": str(slot.date),
        "start_time": str(slot.start_time)
    })
    db.session.delete(slot)
    db.session.commit()
