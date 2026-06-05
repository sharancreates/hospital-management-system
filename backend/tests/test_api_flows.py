import pytest
import json
from models import AuditLog, Treatment
from extensions import db

def test_full_system_api_flow(client, seed_data, app):
    # 1. New Patient registers self
    register_res = client.post('/api/v1/patient/register', json={
        'email': 'flow_patient@test.com',
        'password': 'StrongPatientPass123!',
        'pat_name': 'Flow Patient',
        'gender': 'Male',
        'dob': '1992-08-08',
        'contact_num': '9988776655',
        'age': 34
    })
    assert register_res.status_code == 201

    # 2. Patient logs in
    login_pat_res = client.post('/api/v1/auth/login', json={
        'email': 'flow_patient@test.com',
        'password': 'StrongPatientPass123!'
    })
    assert login_pat_res.status_code == 200
    
    # Logout patient
    client.post('/api/v1/auth/logout')

    # 3. Doctor logs in and sets availability
    login_doc_res = client.post('/api/v1/auth/login', json={
        'email': 'doctor@test.com',
        'password': 'DoctorPassword123!'
    })
    assert login_doc_res.status_code == 200

    set_avail_res = client.post('/api/v1/doctor/set_availability', json={
        'date': '2026-07-01',
        'time_slot': '09:00'
    })
    assert set_avail_res.status_code == 200
    
    client.post('/api/v1/auth/logout')

    # 4. Patient logs back in and books that slot
    client.post('/api/v1/auth/login', json={
        'email': 'flow_patient@test.com',
        'password': 'StrongPatientPass123!'
    })
    
    book_res = client.post('/api/v1/patient/add_appointment', json={
        'doc': seed_data['doctor_id'],
        'date': '2026-07-01',
        'time': '09:00'
    })
    assert book_res.status_code == 200
    book_data = json.loads(book_res.data)
    
    # Verify booking returned success
    assert book_data.get('status') == 'success'
    
    # Logout patient
    client.post('/api/v1/auth/logout')

    # 5. Doctor logs in, views appointments, adds treatment
    client.post('/api/v1/auth/login', json={
        'email': 'doctor@test.com',
        'password': 'DoctorPassword123!'
    })
    
    doc_dash_res = client.get('/api/v1/doctor/')
    assert doc_dash_res.status_code == 200
    doc_dash_data = json.loads(doc_dash_res.data)
    
    appt = doc_dash_data['appointments'][0]
    assert appt['patient_name'] == 'Flow Patient'
    appt_id = appt['appointment_id']

    treatment_res = client.post(f'/api/v1/doctor/add_treatment/{appt_id}', json={
        'ailment': 'Migraine Headaches',
        'prescription': 'Ibuprofen 400mg twice daily',
        'notes': 'Rest in a dark room.'
    })
    assert treatment_res.status_code == 200
    
    client.post('/api/v1/auth/logout')

    # 6. Admin logs in and audits log entries
    client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPassword123!'
    })
    
    # Verify database state inside application context
    with app.app_context():
        # Check treatment was added
        treatment = Treatment.query.filter_by(appointment_id=appt_id).first()
        assert treatment is not None
        assert treatment.ailment == 'Migraine Headaches'
        
        # Check audit logs are recorded for patient booking & treatment
        audit_bookings = AuditLog.query.filter_by(action='BOOK_APPOINTMENT').all()
        assert len(audit_bookings) > 0
