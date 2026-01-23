from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Doctor, Patient, Treatment, Appointment, Availability
from forms import TreatmentForm, AvailabilityForm
from flask_login import login_required, current_user
from extensions import db
from datetime import datetime, date

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@login_required
def doctor_dashboard():
    # Ensure the current user is actually a doctor
    if current_user.role != 'doctor':
        flash('Access denied.', 'danger')
        return redirect(url_for('index')) # or wherever you want non-doctors to go

    doctor = Doctor.query.filter_by(user_id=current_user.user_id).first_or_404()
    
    # In a real app, you might want to filter patients related to this doctor only
    patient = Patient.query.all()
    
    appointments = Appointment.query.filter_by(doctor_id=doctor.doctor_id).order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).all()
    
    return render_template('doctor/dashboard.html', doctor=doctor, appointments=appointments, pats=patient)

@doctor_bp.route('/add_treatment/<int:appointment_id>', methods=['POST', 'GET'])
@login_required
def add_treatment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form = TreatmentForm()
    
    # Verify the logged-in doctor owns this appointment
    doctor_record = Doctor.query.filter_by(user_id=current_user.user_id).first()
    if appointment.doctor_id != doctor_record.doctor_id:
        flash('You are not authorized to treat this appointment.', 'danger')
        return redirect(url_for('doctor.doctor_dashboard'))

    if form.validate_on_submit():
        treatment = Treatment(
            ailment=form.ailment.data,
            prescription=form.prescription.data,
            notes=form.notes.data,
            appointment_id=appointment_id
        )
        
        appointment.status = "Completed"
        db.session.add(treatment)
        db.session.commit()
        
        flash('Treatment added successfully.', 'success')
        return redirect(url_for('doctor.doctor_dashboard'))
        
    return render_template('doctor/treatment.html', form=form, doctor=appointment.doctor, patient=appointment.patient, app=appointment)

@doctor_bp.route('/view_treatment/<int:appointment_id>')
@login_required
def view_treatment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    # Using .first() is safer if you expect one treatment per appointment, 
    # but if multiple are allowed, keep .all() and loop in template.
    treatments = Treatment.query.filter_by(appointment_id=appointment_id).all()
    
    return render_template('doctor/view_treatment.html', 
                           doctor=appointment.doctor, 
                           patient=appointment.patient, 
                           app=appointment, 
                           treatment=treatments)

@doctor_bp.route('/patient_history/<int:patient_id>')
@login_required
def patient_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc()).all()

    return render_template('doctor/patient_history.html', patient=patient, appointment=appointments)

@doctor_bp.route('/set_availability', methods=['GET', 'POST'])
@login_required
def set_availability():
    # Fetch the doctor profile for the current user
    doctor = Doctor.query.filter_by(user_id=current_user.user_id).first_or_404()
    form = AvailabilityForm()

    # Time slot mapping logic
    TIME_SLOTS = {
        "09:00": "11:00",
        "11:00": "13:00",
        "13:00": "15:00",
        "15:00": "17:00",
        "17:00": "19:00",
        "19:00": "21:00"
    }

    if form.validate_on_submit():
        selected_date = form.date.data
        start_time_str = form.time_slot.data
        
        # Convert times
        start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
        end_time_str = TIME_SLOTS[start_time_str]
        end_time_obj = datetime.strptime(end_time_str, "%H:%M").time()

        # Check for duplicates
        exists = Availability.query.filter_by(
            doctor_id=doctor.doctor_id,
            date=selected_date,
            start_time=start_time_obj
        ).first()

        if exists:
            flash("This time slot is already set.", "warning")
        else:
            new_slot = Availability(
                doctor_id=doctor.doctor_id,
                date=selected_date,
                start_time=start_time_obj,
                end_time=end_time_obj
            )
            db.session.add(new_slot)
            db.session.commit()
            flash("Availability added!", "success")
            return redirect(url_for('doctor.set_availability'))

    # Show existing slots
    slots = Availability.query.filter_by(doctor_id=doctor.doctor_id).order_by(Availability.date, Availability.start_time).all()

    return render_template(
        'doctor/set_availability.html',
        form=form,
        doctor=doctor,
        slots=slots,
        today=date.today().isoformat()
    )

@doctor_bp.route('/remove_slot/<int:slot_id>', methods=['POST'])
@login_required
def remove_slot(slot_id):
    slot = Availability.query.get_or_404(slot_id)
    
    # Security: Ensure the doctor deleting the slot actually owns it
    doctor_record = Doctor.query.filter_by(user_id=current_user.user_id).first()
    if not doctor_record or slot.doctor_id != doctor_record.doctor_id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('doctor.doctor_dashboard'))

    db.session.delete(slot)
    db.session.commit()
    flash("Slot removed successfully!", "success")
    return redirect(url_for('doctor.set_availability'))