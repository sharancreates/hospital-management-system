import pytest
from models import User, Patient, Doctor, Department, Appointment, Treatment, Availability, AuditLog
from extensions import db
from datetime import date, datetime, time
from sqlalchemy.exc import IntegrityError

def test_user_password_hashing(app):
    with app.app_context():
        user = User(email="test_hash@example.com")
        user.set_password("SecurePassword123!")
        
        assert user.password_hash != "SecurePassword123!"
        assert user.check_password("SecurePassword123!")
        assert not user.check_password("WrongPassword")

def test_patient_dynamic_age(app):
    with app.app_context():
        # Birth date exactly 30 years ago from today
        today = date.today()
        dob_30 = date(today.year - 30, today.month, today.day)
        
        patient = Patient(
            pat_name="John Doe",
            gender="Male",
            dob=dob_30,
            contact_num="1234567890"
        )
        assert patient.age == 30

def test_cascade_delete_appointment_treatment(app, seed_data):
    with app.app_context():
        # Fetch seeded instances
        doctor = Doctor.query.get(seed_data['doctor_id'])
        patient = Patient.query.get(seed_data['patient_id'])
        
        # Create appointment
        appt = Appointment(
            doctor_id=doctor.doctor_id,
            patient_id=patient.patient_id,
            date=date(2026, 6, 15),
            time=time(10, 0),
            status="Scheduled",
            token_number=1
        )
        db.session.add(appt)
        db.session.commit()
        
        # Create treatment
        treatment = Treatment(
            appointment_id=appt.appointment_id,
            ailment="Common Cold",
            prescription="Rest and fluids",
            notes="Follow up if needed"
        )
        db.session.add(treatment)
        db.session.commit()
        
        # Verify both exist
        assert Appointment.query.get(appt.appointment_id) is not None
        assert Treatment.query.filter_by(appointment_id=appt.appointment_id).first() is not None
        
        # Delete appointment
        db.session.delete(appt)
        db.session.commit()
        
        # Verify appointment AND treatment are both deleted (cascade)
        assert Appointment.query.get(appt.appointment_id) is None
        assert Treatment.query.filter_by(appointment_id=appt.appointment_id).first() is None

def test_unique_availability_constraint(app, seed_data):
    with app.app_context():
        doctor_id = seed_data['doctor_id']
        slot_date = date(2026, 6, 20)
        start_time = time(9, 0)
        end_time = time(9, 30)
        
        # Add first slot
        slot1 = Availability(
            doctor_id=doctor_id,
            date=slot_date,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(slot1)
        db.session.commit()
        
        # Add duplicate slot
        slot2 = Availability(
            doctor_id=doctor_id,
            date=slot_date,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(slot2)
        
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

def test_audit_log_record(app, seed_data):
    with app.app_context():
        log = AuditLog(
            user_id=seed_data['admin_user_id'],
            action="CREATE",
            target_type="Doctor",
            target_id=seed_data['doctor_id'],
            changes='{"email": "doctor@test.com"}'
        )
        db.session.add(log)
        db.session.commit()
        
        saved_log = AuditLog.query.filter_by(user_id=seed_data['admin_user_id']).first()
        assert saved_log is not None
        assert saved_log.action == "CREATE"
        assert saved_log.target_type == "Doctor"
        assert saved_log.changes == '{"email": "doctor@test.com"}'
