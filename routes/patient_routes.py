from flask import Blueprint, request, flash, redirect, url_for, render_template, abort
from models import Patient, User, Doctor, Department, Appointment, Treatment, Availability, MAX_APPOINTMENTS_PER_SLOT
from forms import PatientRegistrationForm, PatientUpdateForm
from datetime import datetime, date
from extensions import db
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

def get_current_patient():
    return Patient.query.filter_by(user_id=current_user.user_id).first()

@patient_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('patient.patient_dashboard'))

    form = PatientRegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists.", "danger")
            return redirect(url_for('patient.register'))
    else:
        if request.method == 'POST':
            # print("Form Validation Failed!")
            # print(form.errors) 
            # flash("Please check the form for errors.", "danger")

            try:
                hashed_pw = generate_password_hash(form.password.data)
                user = User(
                    email=form.email.data,
                    password_hash=hashed_pw,
                    role='patient'
                )
                db.session.add(user)
                db.session.flush()  

                patient = Patient(
                    pat_name=form.pat_name.data,
                    gender=form.gender.data,
                    dob=form.dob.data,
                    contact_num=form.contact_num.data,
                    age=form.age.data,
                    user_id=user.user_id
                )
                db.session.add(patient)
                db.session.commit()
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error during registration: {str(e)}', 'danger')

    return render_template('patient/register.html', form=form)

@patient_bp.route('/dashboard')
@login_required
def patient_dashboard():
    patient = get_current_patient()
    if not patient:
        flash('Patient profile not found.', 'danger')
        return redirect(url_for('index'))
    appointments = Appointment.query.filter_by(patient_id=patient.patient_id).order_by(Appointment.date.desc()).all()
    docs = Doctor.query.all()
    departments = Department.query.all()
    
    return render_template('patient/dashboard.html', 
                           patient=patient, 
                           docs=docs, 
                           appointment=appointments, 
                           department=departments)

@patient_bp.route('/update_patient', methods=['GET', 'POST'])
@login_required
def update_patient():
    patient = get_current_patient()
    if not patient:
        return abort(403)

    form = PatientUpdateForm(obj=patient)

    if form.validate_on_submit():
        patient.pat_name = form.pat_name.data
        patient.gender = form.gender.data
        patient.contact_num = form.contact_num.data
        patient.dob = form.dob.data
        patient.age = form.age.data
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('patient.patient_dashboard'))

    return render_template('patient/update_patient.html', form=form, patient=patient)

@patient_bp.route('/treatment/<int:treatment_id>')
@login_required
def view_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    appointment = treatment.appointment
    current_pat = get_current_patient()
    if not appointment or appointment.patient_id != current_pat.patient_id:
        abort(403)  # Forbidden

    doctor = appointment.doctor
    patient = appointment.patient

    return render_template('patient/view_treatment.html', 
                           app=appointment, 
                           treatment=treatment, 
                           doctor=doctor, 
                           patient=patient)

@patient_bp.route("/add_appointment", methods=["GET", "POST"])
@login_required
def add_appointment():
    patient = get_current_patient()
    doctors = Doctor.query.all()
    selected_doctor = request.form.get("doc")
    selected_date = request.form.get("date")
    selected_slot = request.form.get("slot")
    
    available_slots = []
    if selected_doctor and selected_date:
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            if date_obj < date.today():
                 flash("Cannot book appointments in the past.", "warning")
            else:
                all_slots = Availability.query.filter_by(
                    doctor_id=selected_doctor,
                    date=date_obj
                ).order_by(Availability.start_time).all()

                for s in all_slots:
                    booked_count = Appointment.query.filter_by(
                        doctor_id=selected_doctor,
                        date=date_obj,
                        time=s.start_time
                    ).filter(Appointment.status != 'Cancelled').count() # Ignore cancelled slots
                    
                    if booked_count < 10:
                        available_slots.append(s)

                if not available_slots:
                    flash("No available slots for this doctor on the selected date.", "warning")
        except ValueError:
            flash("Invalid date format.", "danger")
    if request.method == 'POST' and selected_doctor and selected_date and selected_slot:
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            slot = Availability.query.get(selected_slot) # Validating slot existence

            if not slot or str(slot.doctor_id) != str(selected_doctor):
                 flash("Invalid slot selection.", "danger")
                 return redirect(url_for("patient.add_appointment"))

            # FIX: Ensure the slot actually belongs to the selected date!
            if slot.date != date_obj:
                 flash("Slot date mismatch. Please refresh and try again.", "danger")
                 return redirect(url_for("patient.add_appointment"))

            current_count = Appointment.query.filter_by(
                doctor_id=selected_doctor, 
                date=date_obj, 
                time=slot.start_time
            ).filter(Appointment.status != 'Cancelled').count()

            if current_count >= MAX_APPOINTMENTS_PER_SLOT:
                flash("Slot filled up just now! Please pick another.", "danger")
            else:
                new_token = current_count + 1
                new_app = Appointment(
                    patient_id=patient.patient_id,
                    doctor_id=selected_doctor,
                    date=date_obj,
                    time=slot.start_time,
                    status="Booked",
                    token_number=new_token
                )
                db.session.add(new_app)
                db.session.commit()
                flash(f"Appointment Booked! Token: {new_token}", "success")
                return redirect(url_for("patient.patient_dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error booking appointment: {str(e)}", "danger")

    return render_template(
        "patient/add_appointment.html",
        patient=patient,
        doctors=doctors,
        available_slots=available_slots,
        selected_doctor=int(selected_doctor) if selected_doctor else None,
        selected_date=selected_date
    )

@patient_bp.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    app = Appointment.query.get_or_404(appointment_id)
    
    current_pat = get_current_patient()
    if app.patient_id != current_pat.patient_id:
        abort(403)

    app.status = 'Cancelled'
    
    db.session.commit()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('patient.patient_dashboard'))

@patient_bp.route('/doc_profile/<int:doctor_id>')
@login_required
def doc_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
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
            free_slots.append(slot)

    return render_template("patient/doctor_profile.html", doctor=doctor, free_slots=free_slots)