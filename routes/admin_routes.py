from flask import Blueprint, request, flash, redirect, url_for, render_template
from models import Patient, User, Department, Doctor, Appointment, Treatment
from forms import DoctorForm, PatientForm, AppointmentForm
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash
from flask_login import login_required

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

            default_password = "doctor123"
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


@admin_bp.route('/set_appointment', methods=['GET', 'POST'])
@login_required
def set_appointment():
    form = AppointmentForm()
    form.doctor.choices = [(d.doctor_id, d.doc_name) for d in Doctor.query.all()]
    form.patient.choices = [(p.patient_id, p.pat_name) for p in Patient.query.all()]

    if form.validate_on_submit():
        existing_appt = Appointment.query.filter_by(
            doctor_id=form.doctor.data, 
            date=form.date.data, 
            time=form.time.data
        ).first()

        if existing_appt and existing_appt.status != 'Cancelled':
            flash('This doctor is already booked for that time.', 'warning')
        else:
            new_appt = Appointment(
                patient_id=form.patient.data,
                doctor_id=form.doctor.data,
                date=form.date.data,
                time=form.time.data,
                status='Booked'
            )
            db.session.add(new_appt)
            db.session.commit()
            flash('Appointment scheduled successfully', 'success')
            return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_appointment.html', form=form)


@admin_bp.route('/completed/<int:appointment_id>', methods=['POST'])
@login_required
def complete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'Completed'
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/cancelled/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'Cancelled'
    db.session.commit()
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