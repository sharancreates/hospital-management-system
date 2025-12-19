from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from models import Doctor, Patient, Treatment, Appointment, Availability
from flask_login import login_required, current_user
from extensions import db
from datetime import datetime, date
from datetime import date as dt_date 

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@login_required
def doctor_dashboard():
    doctor = Doctor.query.filter_by(user_id=current_user.user_id).first_or_404()
    patient = Patient.query.all()
    appointments = Appointment.query.filter_by(doctor_id=doctor.doctor_id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return render_template('doctor/dashboard.html', doctor = doctor, appointments = appointments, pats=patient)

@doctor_bp.route('/add_treatment/<int:appointment_id>', methods = ['POST', 'GET'])
@login_required
def add_treatment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = appointment.doctor 
    patient = appointment.patient

    if request.method == 'POST':
        ailment = request.form['ailment']
        prescription = request.form['prescription']
        notes = request.form['notes']

        treatment = Treatment(
            ailment = ailment,
            prescription = prescription,
            notes = notes,
            appointment_id = appointment_id
        )
        
        appointment.status = "Completed"
        db.session.add(treatment)
        db.session.commit()
        return redirect(url_for('doctor.doctor_dashboard'))
    return render_template('doctor/treatment.html', doctor = doctor, patient = patient, app = appointment)                  

@doctor_bp.route('/view_treatment/<int:appointment_id>')
@login_required
def view_treatment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = appointment.doctor
    patient = appointment.patient

    treatment = Treatment.query.filter_by(appointment_id = appointment_id).all()
    return render_template('doctor/view_treatment.html', doctor=doctor, patient=patient, app=appointment, treatment = treatment)

@doctor_bp.route('/patient_history/<int:patient_id>')
@login_required
def patient_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appointment = Appointment.query.filter_by(patient_id = patient_id).order_by(Appointment.date.desc()).all()

    return render_template('doctor/patient_history.html',patient=patient,appointment=appointment)


@doctor_bp.route('/<int:doctor_id>/set_availability', methods=['GET', 'POST'])
@login_required
def set_availability(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    TIME_SLOTS = {
        "09:00": "11:00",
        "11:00": "13:00",
        "13:00": "15:00",
        "15:00": "17:00",
        "17:00": "19:00",
        "19:00": "21:00"
    }

    if request.method == 'POST':
        selected_date_str = request.form.get("date")
        selected_start = request.form.get("time")

        # Convert date string → Python date
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

        # Convert string → Python time
        start_time_obj = datetime.strptime(selected_start, "%H:%M").time()
        end_time_obj = datetime.strptime(TIME_SLOTS[selected_start], "%H:%M").time()

        # Prevent duplicate slot
        exists = Availability.query.filter_by(
            doctor_id=doctor_id,
            date=selected_date,
            start_time=start_time_obj
        ).first()

        if exists:
            flash("This slot already exists!", "warning")
            return redirect(request.url)

        new_slot = Availability(
            doctor_id=doctor_id,
            date=selected_date,
            start_time=start_time_obj,
            end_time=end_time_obj
        )

        db.session.add(new_slot)
        db.session.commit()

        flash("Availability added!", "success")
        return redirect(request.url)

    slots = Availability.query.filter_by(doctor_id=doctor_id).all()

    return render_template(
        'doctor/set_availability.html',
        doctor=doctor,
        slots=slots,
        TIME_SLOTS=TIME_SLOTS,
        today=date.today().isoformat()
    )

@doctor_bp.route('/remove_slot/<int:slot_id>')
@login_required
def remove_slot(slot_id):
    slot = Availability.query.get_or_404(slot_id)
    db.session.delete(slot)
    db.session.commit()
    flash("Slot removed successfully!", "success")
    return redirect(url_for('doctor.set_availability', doctor_id=slot.doctor_id))
