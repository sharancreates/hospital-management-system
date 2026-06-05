import pytest
import json
from models import Doctor, Patient, User
from unittest.mock import patch

def login_admin(client):
    client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPassword123!'
    })

def test_get_doctors_paginated_and_eager_loaded(client, seed_data):
    # Log in as admin
    login_admin(client)
    
    response = client.get('/api/v1/admin/doctors?page=1&per_page=10')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('status') == 'success'
    assert 'doctors' in data
    assert len(data['doctors']) == 1
    assert data['doctors'][0]['doc_name'] == 'Dr. Test House'
    assert data['doctors'][0]['department'] == 'Cardiology'

@patch('services.admin_service.mail.send')
def test_add_doctor_success(mock_send_mail, client, seed_data):
    login_admin(client)
    
    response = client.post('/api/v1/admin/add_doctor', json={
        'doc_name': 'Dr. Watson',
        'gender': 'Male',
        'contact_num': '1234509876',
        'specialization': seed_data['cardio_id'],
        'dob': '1975-04-12'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('status') == 'success'
    assert "Doctor added successfully" in data.get('message')
    assert mock_send_mail.called

def test_add_doctor_validation_error(client, seed_data):
    login_admin(client)
    
    # Missing doctor name
    response = client.post('/api/v1/admin/add_doctor', json={
        'gender': 'Male',
        'contact_num': '1234509876',
        'specialization': seed_data['cardio_id'],
        'dob': '1975-04-12'
    })
    assert response.status_code == 400
    assert "Doctor Name is required" in json.loads(response.data).get('message')

def test_update_doctor(client, seed_data):
    login_admin(client)
    
    response = client.post(f"/api/v1/admin/update_doctor/{seed_data['doctor_id']}", json={
        'doc_name': 'Dr. House MD'
    })
    assert response.status_code == 200
    
    # Verify update
    response_list = client.get('/api/v1/admin/doctors')
    data = json.loads(response_list.data)
    assert data['doctors'][0]['doc_name'] == 'Dr. House MD'

def test_delete_doctor(client, seed_data, app):
    login_admin(client)
    
    response = client.delete(f"/api/v1/admin/delete_doctor/{seed_data['doctor_id']}")
    assert response.status_code == 200
    
    # Doctor account role should be deactivated or user deleted
    with app.app_context():
        doc_user = User.query.get(seed_data['doctor_user_id'])
        # If cascading or deactivation is done:
        assert doc_user is None or doc_user.role == 'inactive'

def test_unauthorized_admin_access(client, seed_data):
    # Log in as normal patient instead of admin
    client.post('/api/v1/auth/login', json={
        'email': 'patient@test.com',
        'password': 'PatientPassword123!'
    })
    
    response = client.get('/api/v1/admin/doctors')
    # Expect 403 Forbidden
    assert response.status_code == 403
