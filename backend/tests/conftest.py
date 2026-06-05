import pytest
import os
import sys

# Ensure backend root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import Department, User, Doctor, Patient
from werkzeug.security import generate_password_hash
from datetime import datetime, date

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False  # Disable CSRF in tests for ease of API invocation
    WTF_CSRF_CHECK_DEFAULT = False
    SESSION_COOKIE_SECURE = False
    RATELIMIT_ENABLED = False

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function', autouse=True)
def clean_db(app):
    with app.app_context():
        # Clear existing table records
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield

@pytest.fixture(scope='function')
def seed_data(app):
    with app.app_context():
        # Seed departments
        cardio = Department(department_name='Cardiology', description='Heart services')
        peds = Department(department_name='Pediatrics', description='Children services')
        db.session.add_all([cardio, peds])
        db.session.commit()

        # Seed admin
        admin_user = User(
            email='admin@test.com',
            password_hash=generate_password_hash('AdminPassword123!'),
            role='admin'
        )
        db.session.add(admin_user)

        # Seed doctor
        doc_user = User(
            email='doctor@test.com',
            password_hash=generate_password_hash('DoctorPassword123!'),
            role='doctor'
        )
        db.session.add(doc_user)
        db.session.commit()

        doc_profile = Doctor(
            doc_name='Dr. Test House',
            gender='Male',
            dob=date(1980, 1, 1),
            contact_num='1234567890',
            user_id=doc_user.user_id,
            department_id=cardio.department_id
        )
        db.session.add(doc_profile)
        db.session.commit()

        # Seed patient
        pat_user = User(
            email='patient@test.com',
            password_hash=generate_password_hash('PatientPassword123!'),
            role='patient'
        )
        db.session.add(pat_user)
        db.session.commit()

        pat_profile = Patient(
            pat_name='John Doe',
            gender='Male',
            dob=date(1990, 5, 15),
            contact_num='0987654321',
            user_id=pat_user.user_id
        )
        db.session.add(pat_profile)
        db.session.commit()

        return {
            'cardio_id': cardio.department_id,
            'peds_id': peds.department_id,
            'admin_user_id': admin_user.user_id,
            'doctor_user_id': doc_user.user_id,
            'doctor_id': doc_profile.doctor_id,
            'patient_user_id': pat_user.user_id,
            'patient_id': pat_profile.patient_id
        }
