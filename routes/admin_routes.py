from flask import Flask, Blueprint, request, flash, redirect, url_for, render_template
from models import Patient, User, Department, Doctor, Appointment, Treatment
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash
from flask_login import login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/add_doctor', methods=['GET', 'POST', 'DELETE'])
def add_doctor():
    department = Department.query.all()
    if request.method == 'POST':
        doc_name = request.form['doc-name']
        gender = request.form['gender']
        contact = request.form['contact_num']
        dob_str = request.form['dob']
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        specialization_id = request.form.get('specialization')

        default_password = "doctor123"
        hashed_pw = generate_password_hash(default_password)
        base_email = f"{doc_name.lower().replace(' ', '.')}"
        email = f"{base_email}@arogya.in"
        count = 1
        while User.query.filter_by(email = email).first():
            email = f"{base_email}.{count}@arogya.in"
            count += 1
        user = User(
            email = email,
            password_hash = hashed_pw,
            role = 'doctor'
        )
        db.session.add(user)
        db.session.commit()

        doctor = Doctor(
            doc_name = doc_name,
            gender = gender,
            dob = dob,
            contact_num = contact,
            specialization = specialization_id,
            user_id = user.user_id
        )
        db.session.add(doctor)
        db.session.commit()

        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/add_doctor.html', department = department)

@admin_bp.route("/delete_doctor/<int:doctor_id>")
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route("/update_doctor/<int:doctor_id>", methods = ['GET', 'POST'])
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    department = Department.query.all()

    if request.method == 'POST':
        doctor.doc_name = request.form['doc-name']
        doctor.gender = request.form['gender']
        doctor.contact_num = request.form['contact_num']
        dob_str = request.form['dob']
        doctor.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        doctor.specialization = request.form.get('specialization')
            
        db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))

    return render_template(
        'admin/update_doctor.html', 
        doctor = doctor, department = department
    )

@admin_bp.route('/', methods = ['GET', 'POST'])
@login_required
def admin_dashboard():
    docs = Doctor.query.all()
    pats = Patient.query.all()
    app = Appointment.query.all()
    return render_template('admin/dashboard.html', docs = docs, pats = pats, appointments = app, doctor_results=None, patient_results=None, query=None)

@admin_bp.route('/set_appointment', methods = ['POST', 'GET'])
@login_required
def set_appointment():
    docs = Doctor.query.all()
    pats = Patient.query.all()
    if request.method == 'POST':
        doc = request.form.get('doc')
        pat = request.form.get('pat')

        if not doc or not pat:
            flash('Please select both a doctor and a patient.', 'warning')
            print("NO")
            return redirect(url_for('admin.set_appointment'))
        
        doc = int(doc)
        pat = int(pat)
        date = request.form['date']
        apdate = datetime.strptime(date, '%Y-%m-%d').date()
        time = request.form['time']
        aptime = datetime.strptime(time, '%H:%M').time()

        appointments = Appointment(
            patient_id = pat,
            doctor_id = doc,
            date = apdate,
            time = aptime,
            status = 'Booked'
        )
        db.session.add(appointments)
        db.session.commit()

        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/add_appointment.html', doctors = docs, patients = pats)

@admin_bp.route('/completed/<int:appointment_id>', methods = ['POST', 'GET'])
def complete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.status = 'Completed'

    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/cancelled/<int:appointment_id>', methods = ['POST', 'GET'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.status = 'Cancelled'

    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/treatment/<int:treatment_id>')
def view_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    appointment = treatment.appointment

    doctor = appointment.doctor if appointment else None
    patient = appointment.patient if appointment else None

    return render_template(
        'admin/view_treatment.html',
        app=appointment,
        treatment=treatment,
        doctor=doctor,
        patient=patient
    )

@admin_bp.route('/searchdocs')
def searchdocs():
    query = request.args.get('q', '').strip().lower()

    doctors = Doctor.query.all()
    patients = Patient.query.all()
    appointments = Appointment.query.all()

    if not query:
        return redirect(url_for('admin.admin_dashboard'))

    doctor_results = [
        d for d in doctors
        if query in d.doc_name.lower() or query == str(d.doctor_id)
    ]

    return render_template(
        'admin/dashboard.html',
        docs=doctors,
        pats=patients,
        appointments=appointments,
        doctor_results=doctor_results,
        patient_results=None,
        query=query
    )


@admin_bp.route('/searchpats')
def searchpats():
    query = request.args.get('p', '').strip().lower()

    doctors = Doctor.query.all()
    patients = Patient.query.all()
    appointments = Appointment.query.all()

    if not query:
        return redirect(url_for('admin.admin_dashboard'))

    patient_results = [
        p for p in patients
        if query in p.pat_name.lower() or query == str(p.patient_id)
    ]

    return render_template(
        'admin/dashboard.html',
        docs=doctors,
        pats=patients,
        appointments=appointments,
        doctor_results=None,
        patient_results=patient_results,
        query=query
    )

@admin_bp.route('/update_patient/<int:patient_id>', methods = ['POST', 'GET'])
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        patient.doc_name = request.form['pat_name']
        patient.gender = request.form['gender']
        patient.contact_num = request.form['contact_num']
        dob_str = request.form['dob']
        patient.age = request.form['age']
        patient.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            
        db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))

    return render_template(
        'admin/update_patient.html', 
        patient = patient
    )

@admin_bp.route("/delete_patient/<int:patient_id>")
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))