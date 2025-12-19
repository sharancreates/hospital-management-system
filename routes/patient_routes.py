from flask import Flask, Blueprint, request, flash, redirect, url_for, render_template
from models import Patient, User, Doctor, Department, Appointment, Treatment, Availability
from datetime import datetime
from extensions import db
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

TIME_SLOTS = {
    "1": "9AM TO 11AM",
    "2": "11AM TO 1PM",
    "3": "1PM TO 3PM",
    "4": "3PM TO 5PM",
    "5": "5PM TO 7PM",
    "6": "7PM TO 9PM"
}

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['pat_name']
        gender = request.form['gender']
        contact = request.form['contact_num']
        dob_str = request.form['dob']
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        hashed_pw = generate_password_hash(password)

        if User.query.filter_by(email = email).first():
            flash("Email already exists.", "danger")
            return redirect(url_for('patient.register'))

        user = User(
            email = email,
            password_hash = hashed_pw,
            role = 'patient'
        )
        db.session.add(user)
        db.session.commit()

        patient = Patient(
            pat_name = name,
            gender = gender,
            dob = dob,
            contact_num = contact,
            user_id = user.user_id,
            age = age
        )
        db.session.add(patient)
        db.session.commit()
        return redirect(url_for('patient.patient_dashboard', patient_id = patient.patient_id))
    
    return render_template('patient/register.html')
        
@patient_bp.route('/dashboard')
@login_required
def patient_dashboard():
    patient = Patient.query.filter_by(user_id=current_user.user_id).first_or_404()
    docs = Doctor.query.all()
    department = Department.query.all()
    pat_id = patient.patient_id
    appointment = Appointment.query.filter_by(patient_id = patient.patient_id).all()
    #appointments = Appointment.query.filter_by(doctor_id=doctor.doctor_id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return render_template('patient/dashboard.html', patient = patient, docs = docs, appointment=appointment, department=department)

@patient_bp.route('update_patient/<int:patient_id>', methods = ['POST', 'GET'])
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        patient.pat_name = request.form['pat-name']
        patient.gender = request.form['gender']
        patient.contact_num = request.form['contact_num']
        dob_str = request.form['dob']
        patient.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        patient.age = request.form['age']
            
        db.session.commit()
        return redirect(url_for('patient.patient_dashboard'))

    return render_template('patient/update_patient.html', patient = patient)

@patient_bp.route('/treatment/<int:treatment_id>')
def view_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    appointment = treatment.appointment

    doctor = appointment.doctor if appointment else None
    patient = appointment.patient if appointment else None

    return render_template(
        'patient/view_treatment.html',
        app=appointment,
        treatment=treatment,
        doctor=doctor,
        patient=patient
    )

MAX_APPOINTMENTS_PER_SLOT = 2

@patient_bp.route("/add_appointment", methods=["GET", "POST"])
@login_required
def add_appointment():
    patient = Patient.query.filter_by(user_id=current_user.user_id).first_or_404()
    doctors = Doctor.query.all()

    selected_doctor = request.form.get("doc")
    selected_date = request.form.get("date")
    selected_slot = request.form.get("slot")

    available_slots = []

    if selected_doctor and selected_date and not selected_slot:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

        all_slots = Availability.query.filter_by(
            doctor_id=selected_doctor,
            date=date_obj
        ).order_by(Availability.start_time).all()

        for s in all_slots:
            booked_count = Appointment.query.filter_by(
                doctor_id=selected_doctor,
                date=date_obj,
                time=s.start_time
            ).count()
            if booked_count < MAX_APPOINTMENTS_PER_SLOT:
                available_slots.append(s)

        if not available_slots:
            flash("No available slots for this doctor on the selected date.", "warning")

    if selected_doctor and selected_date and selected_slot:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        slot = Availability.query.get(selected_slot)

        booked_count = Appointment.query.filter_by(
            doctor_id=selected_doctor,
            date=date_obj,
            time=slot.start_time
        ).count()

        if booked_count >= MAX_APPOINTMENTS_PER_SLOT:
            flash("This time slot is fully booked. Please select another slot.", "danger")
            return redirect(url_for("patient.add_appointment"))

        new_appointment = Appointment(
            patient_id=patient.patient_id,
            doctor_id=selected_doctor,
            date=date_obj,
            time=slot.start_time,
            status="booked"
        )
        db.session.add(new_appointment)
        db.session.commit()

        flash("Appointment booked successfully!", "success")
        return redirect(url_for("patient.patient_dashboard"))

    return render_template(
        "patient/add_appointment.html",
        patient=patient,
        doctors=doctors,
        available_slots=available_slots,
        selected_doctor=int(selected_doctor) if selected_doctor else None,
        selected_date=selected_date
    )

@patient_bp.route('/cancel_appointment/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    app = Appointment.query.get_or_404(appointment_id)
    db.session.delete(app)
    db.session.commit()
    return redirect(url_for('patient.patient_dashboard'))

@patient_bp.route('/doc_profile/<int:doctor_id>')
def doc_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template("patient/doctor_profile.html", doctor = doctor)
