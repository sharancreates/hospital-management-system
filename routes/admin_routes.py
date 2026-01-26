from flask import Blueprint, request, flash, redirect, url_for, render_template
from datetime import datetime, date
from werkzeug.security import generate_password_hash
from flask_login import login_required
import string
from extensions import db
from models import Patient, User, Department, Doctor, Appointment, Treatment, MAX_APPOINTMENTS_PER_SLOT, Availability
from forms import DoctorForm, PatientForm, AppointmentForm
import secrets

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET'])
@login_required
def admin_dashboard():
    docs = Doctor.query.all()
    pats = Patient.query.all()
    app = Appointment.query.all()
    return render_template('admin/dashboard.html', docs=docs, pats=pats, appointments=app, doctor_results=None, patient_results=None, query=None)

@admin_bp.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    form = DoctorForm()
    form.specialization.choices = [(d.department_id, d.department_name) for d in Department.query.all()]

    if form.validate_on_submit():
        try:
            base_email = f"{form.doc_name.data.lower().replace(' ', '.')}@arogya.in"
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

            doctor = Doctor(
                doc_name=form.doc_name.data,
                gender=form.gender.data,
                dob=form.dob.data,
                contact_num=form.contact_num.data,
                department_id=form.specialization.data, 
                user_id=user.user_id
            )
            
            db.session.add(doctor)
            db.session.commit() 
            
            flash(f'Doctor added! Email: {email} | Password: {default_password}', 'success')
            return redirect(url_for('admin.admin_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding doctor: {str(e)}', 'danger')

    return render_template('admin/add_doctor.html', form=form)


@admin_bp.route("/update_doctor/<int:doctor_id>", methods=['GET', 'POST'])
@login_required
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    form = DoctorForm(obj=doctor) #prefill
    form.specialization.choices = [(d.department_id, d.department_name) for d in Department.query.all()]

    if form.validate_on_submit():
        form.populate_obj(doctor) 
        db.session.commit()
        flash('Doctor updated successfully', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/update_doctor.html', form=form, doctor=doctor)


@admin_bp.route("/delete_doctor/<int:doctor_id>", methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.user_id:
        user = User.query.get(doctor.user_id)
        if user:
            db.session.delete(user)
    
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor deleted', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/update_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm(obj=patient)

    if form.validate_on_submit():
        patient.pat_name = form.pat_name.data 
        patient.gender = form.gender.data
        patient.contact_num = form.contact_num.data
        patient.dob = form.dob.data
        patient.age = form.age.data
        
        db.session.commit()
        flash('Patient updated successfully', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/update_patient.html', form=form, patient=patient)


@admin_bp.route("/delete_patient/<int:patient_id>", methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted', 'success')
    return redirect(url_for('admin.admin_dashboard'))

from flask import jsonify

@admin_bp.route('/get_slots/<int:doctor_id>/<string:date_str>')
@login_required
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

            if booked_count < 10:
                time_str = slot.start_time.strftime("%H:%M") 
                available_times.append({
                    "time": time_str,
                    "display": slot.start_time.strftime("%I:%M %p"), 
                    "remaining": 10 - booked_count
                })
        
        return jsonify({"slots": available_times})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.route('/set_appointment', methods=['GET', 'POST'])
@login_required
def set_appointment():
    form = AppointmentForm()
    form.doctor.choices = [(d.doctor_id, d.doc_name) for d in Doctor.query.all()]
    form.patient.choices = [(p.patient_id, p.pat_name) for p in Patient.query.all()]

    if form.validate_on_submit():
        doctor_id = form.doctor.data
        patient_id = form.patient.data
        selected_date = form.date.data
        selected_time = form.time.data 
        if selected_date < date.today():
             flash("Cannot book appointments in the past.", "warning")
             return render_template('admin/add_appointment.html', form=form)
        valid_slot = Availability.query.filter_by(
            doctor_id=doctor_id,
            date=selected_date,
            start_time=selected_time
        ).first()

        if not valid_slot:
            flash(f"Invalid Slot! Doctor is not available at {selected_time.strftime('%I:%M %p')} on this date.", "danger")
            flash("Please check the Doctor's availability schedule (e.g., 09:00, 11:00).", "info")
            return render_template('admin/add_appointment.html', form=form)

        current_count = Appointment.query.filter_by(
            doctor_id=doctor_id, 
            date=selected_date, 
            time=selected_time
        ).filter(Appointment.status != 'Cancelled').count()

        if current_count >= 10:
            flash(f'Slot at {selected_time.strftime("%I:%M %p")} is fully booked (Max {MAX_APPOINTMENTS_PER_SLOT}).', 'warning')
        else:
            try:
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
                db.session.commit()
                
                flash(f'Appointment scheduled successfully! Token: {new_token}', 'success')
                return redirect(url_for('admin.admin_dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Database error: {str(e)}", "danger")

    return render_template('admin/add_appointment.html', form=form)
@admin_bp.route('/completed/<int:appointment_id>', methods=['POST'])
@login_required
def complete_appointment(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = 'Completed'
        db.session.commit()
        flash('Appointment marked as completed.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating status: {str(e)}', 'danger')
        
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/cancelled/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling appointment: {str(e)}', 'danger')
        
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/treatment/<int:treatment_id>')
@login_required
def view_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    appointment = treatment.appointment
    doctor = appointment.doctor if appointment else None
    patient = appointment.patient if appointment else None

    return render_template('admin/view_treatment.html', app=appointment, treatment=treatment, doctor=doctor, patient=patient)


@admin_bp.route('/searchdocs')
@login_required
def searchdocs():
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('admin.admin_dashboard'))

    doctor_results = Doctor.query.filter(
        Doctor.doc_name.ilike(f'%{query}%')
    ).all()

    return render_template('admin/dashboard.html', 
                           docs=Doctor.query.all(), 
                           pats=Patient.query.all(), 
                           appointments=Appointment.query.all(), 
                           doctor_results=doctor_results, 
                           patient_results=None, 
                           query=query)


@admin_bp.route('/searchpats')
@login_required
def searchpats():
    query = request.args.get('p', '').strip()

    if not query:
        return redirect(url_for('admin.admin_dashboard'))

    patient_results = Patient.query.filter(
        Patient.pat_name.ilike(f'%{query}%')
    ).all()

    return render_template('admin/dashboard.html', 
                           docs=Doctor.query.all(), 
                           pats=Patient.query.all(), 
                           appointments=Appointment.query.all(), 
                           doctor_results=None, 
                           patient_results=patient_results, 
                           query=query)