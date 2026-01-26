import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import User, Doctor, Patient, Appointment, Availability, Department
from flask_login import login_user
import unittest
from datetime import date, time, timedelta

class TestFixes(unittest.TestCase):
    def setUp(self):
        # Force in-memory DB by setting env var before create_app
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for easier testing of logic
        # Ensure config is definitely memory, though env var should handle it
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Setup basic data
        self.dept = Department(department_name="General", description="Gen")
        db.session.add(self.dept)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_doctor_form_validation_fix(self):
        """Test that DoctorForm accepts 10-15 digit phone numbers."""
        from forms import DoctorForm
        with self.app.test_request_context():
            form = DoctorForm()
            form.doc_name.data = "Dr. Test"
            form.gender.data = "Male"
            form.dob.data = date(1980, 1, 1)
            form.specialization.data = self.dept.department_id
            
            # Test 10 digits (previously failed if logic was wrong, but original requirement said 10, now 10-15)
            form.contact_num.data = "9876543210" 
            form.submit.data = True # Fake submit
            
            # We just manually validate the field
            form.contact_num.validate(form)
            self.assertFalse(form.contact_num.errors, f"10 digits should be valid: {form.contact_num.errors}")

            # Test 12 digits
            form.contact_num.data = "919876543210"
            form.contact_num.validate(form)
            self.assertFalse(form.contact_num.errors, f"12 digits should be valid: {form.contact_num.errors}")

    def test_admin_appointment_token_logic(self):
        """Test that Admin set_appointment generates a token number."""
        # Create Admin
        admin = User(email='admin@test.com', role='admin', password_hash='hash')
        db.session.add(admin)
        
        # Create Doctor
        doc_user = User(email='doc@test.com', role='doctor', password_hash='hash')
        db.session.add(doc_user)
        db.session.commit()
        
        doctor = Doctor(doc_name="Dr. Who", gender="Male", dob=date(1980,1,1), contact_num="1234567890", user_id=doc_user.user_id, department_id=self.dept.department_id)
        db.session.add(doctor)
        
        # Create Patient
        pat_user = User(email='pat@test.com', role='patient', password_hash='hash')
        db.session.add(pat_user)
        db.session.commit()
        
        patient = Patient(pat_name="John Doe", gender="Male", dob=date(1990,1,1), contact_num="1234567890", age=30, user_id=pat_user.user_id)
        db.session.add(patient)
        db.session.commit()

        # Login as Admin
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(admin.user_id)
            sess['_fresh'] = True

        # Post appointment
        resp = self.client.post('/admin/set_appointment', data={
            'doctor': doctor.doctor_id,
            'patient': patient.patient_id,
            'date': date.today().isoformat(),
            'time': '10:00'
        }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        
        # Check if Appointment exists and has token 1
        appt = Appointment.query.first()
        self.assertIsNotNone(appt)
        self.assertEqual(appt.token_number, 1)

    def test_patient_slot_mismatch_logic(self):
        """Test that patient cannot book a slot from a different date."""
        # Create Data
        pat_user = User(email='pat@test.com', role='patient', password_hash='hash')
        db.session.add(pat_user)
        db.session.commit()
        patient = Patient(pat_name="John", gender="Male", dob=date(1990,1,1), contact_num="1234567890", age=30, user_id=pat_user.user_id)
        db.session.add(patient)

        doc_user = User(email='doc@test.com', role='doctor', password_hash='hash')
        db.session.add(doc_user)
        db.session.commit()
        doctor = Doctor(doc_name="Dr. Who", gender="Male", dob=date(1980,1,1), contact_num="1234567890", user_id=doc_user.user_id, department_id=self.dept.department_id)
        db.session.add(doctor)
        db.session.commit()

        # Create Availability for tomorrow
        tomorrow = date.today() + timedelta(days=1)
        avail = Availability(doctor_id=doctor.doctor_id, date=tomorrow, start_time=time(9,0), end_time=time(11,0))
        db.session.add(avail)
        db.session.commit()
        
        # Login Patient
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(pat_user.user_id)
            sess['_fresh'] = True

        # Try to book for TODAY using TOMORROW's slot
        today = date.today().isoformat()
        
        resp = self.client.post('/patient/add_appointment', data={
            'doc': doctor.doctor_id,
            'date': today, # Mismatch!
            'slot': avail.id
        }, follow_redirects=True)

        # Should fail and flash error
        self.assertIn(b'Slot date mismatch', resp.data)
        self.assertEqual(Appointment.query.count(), 0)

if __name__ == '__main__':
    unittest.main()
