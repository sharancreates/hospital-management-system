import pytest
import json
from models import Patient, User, Appointment, Availability
from extensions import db
from datetime import date, time

def login_patient(client):
    client.post('/api/v1/auth/login', json={
        'email': 'patient@test.com',
        'password': 'PatientPassword123!'
    })

def test_patient_self_registration_success(client):
    response = client.post('/api/v1/patient/register', json={
        'email': 'new_patient@test.com',
        'password': 'StrongNewPass123!',
        'pat_name': 'New Patient Name',
        'gender': 'Female',
        'dob': '1995-10-10',
        'contact_num': '1122334455',
        'age': 30
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data.get('status') == 'success'
    assert "successful" in data.get('message')

def test_patient_self_registration_validation_fails(client):
    # Weak password, invalid email
    response = client.post('/api/v1/patient/register', json={
        'email': 'bademail',
        'password': 'weak',
        'pat_name': 'New Patient Name',
        'gender': 'Female',
        'dob': '1995-10-10',
        'contact_num': '1122334455',
        'age': 30
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data.get('status') == 'error'

def test_patient_book_appointment_success(client, seed_data, app):
    # Register slot in availability first
    with app.app_context():
        slot = Availability(
            doctor_id=seed_data['doctor_id'],
            date=date(2026, 6, 25),
            start_time=time(10, 0),
            end_time=time(10, 30)
        )
        db.session.add(slot)
        db.session.commit()
        
    login_patient(client)
    
    response = client.post('/api/v1/patient/add_appointment', json={
        'doc': seed_data['doctor_id'],
        'date': '2026-06-25',
        'time': '10:00'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('status') == 'success'
    assert "Booked" in data.get('message')
